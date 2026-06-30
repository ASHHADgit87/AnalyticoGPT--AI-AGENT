import streamlit as st
import streamlit.components.v1 as components
import os
import numpy as np


def _heatmap_skip_reason(pipeline_result: dict) -> str:
    corr = pipeline_result.get("correlation_matrix", {})
    descriptive_stats = pipeline_result.get("descriptive_stats", {})
    n_metrics = len(descriptive_stats)

    if n_metrics < 2:
        return (
            "A correlation heatmap requires at least two numeric metric columns to measure "
            "relationships between variables. "
            "Your dataset contains only one numeric column, so there is no pair to correlate."
        )

    if corr:
        non_diag_vals = []
        cols = list(corr.keys())
        for ca in cols:
            for cb in cols:
                if ca != cb:
                    non_diag_vals.append(abs(corr[ca].get(cb, 0.0)))
        if non_diag_vals and max(non_diag_vals) < 0.15:
            return (
                "The correlation matrix was computed but every pair of columns has an absolute "
                "correlation coefficient below 0.15, indicating no meaningful linear or monotonic "
                "relationship exists. Displaying a heatmap of near-zero values would be misleading."
            )

    if pipeline_result.get("mixed_units_detected"):
        return (
            "Mixed unit types were detected in the value column (e.g. currency mixed with "
            "percentage ratios). Averaging incompatible units produces statistically invalid "
            "coefficients, so the heatmap was suppressed."
        )

    return (
        "The dataset structure does not contain the minimum two independent numeric metric "
        "columns needed to build a meaningful correlation heatmap. "
        "The pipeline routed this data to a different chart type instead."
    )


def _trend_skip_reason(pipeline_result: dict) -> str:
    descriptive_stats = pipeline_result.get("descriptive_stats", {})
    n_metrics = len(descriptive_stats)
    time_col = pipeline_result.get("time_col")

    if not time_col:
        return (
            "A trend chart requires a temporal column such as Year, Date, Month, or Quarter "
            "to serve as the x-axis. No such column was detected in your dataset, so plotting "
            "a time series is not possible."
        )

    if n_metrics == 0:
        return (
            "No valid numeric metric column was found to plot on the y-axis. "
            "The trend chart needs at least one numeric column with more than one distinct value."
        )

    return (
        "The dataset structure does not satisfy the conditions for a trend line chart based on "
        "the 14-case visualization decision matrix. The detected column types were routed to "
        "a more appropriate chart type for this data shape."
    )


def _bar_skip_reason(pipeline_result: dict) -> str:
    descriptive_stats = pipeline_result.get("descriptive_stats", {})
    n_metrics = len(descriptive_stats)
    cat_col = pipeline_result.get("categorical_col")

    if not cat_col:
        return (
            "A bar chart requires a categorical column (such as Region, Department, or Product) "
            "to define the groups on the x-axis. No categorical column was found in your dataset."
        )

    if n_metrics == 0:
        return (
            "No numeric metric column was available to measure bar heights. "
            "A bar chart needs at least one numeric column paired with a categorical column."
        )

    return (
        "After grouping and aggregation, all category values produced identical metric heights "
        "with zero visible variance. Rendering a flat uniform bar chart provides no analytical "
        "value, so it was suppressed."
    )


def _heatmap_explanation(pipeline_result: dict) -> str:
    corr = pipeline_result.get("correlation_matrix", {})
    method = pipeline_result.get("corr_method_label", "Pearson")

    best_pair = ("—", "—", 0.0)
    cols = list(corr.keys())
    seen = set()
    for ca in cols:
        for cb, val in corr.get(ca, {}).items():
            if ca != cb and (cb, ca) not in seen:
                seen.add((ca, cb))
                if abs(val) > abs(best_pair[2]):
                    best_pair = (ca, cb, val)

    direction = "positive" if best_pair[2] >= 0 else "negative"
    strength = (
        "very strong"
        if abs(best_pair[2]) >= 0.8
        else (
            "strong"
            if abs(best_pair[2]) >= 0.6
            else "moderate" if abs(best_pair[2]) >= 0.4 else "weak"
        )
    )

    lines = [
        f"Each cell in this matrix shows the {method} correlation coefficient (r) between two numeric columns, ranging from -1 (perfect negative relationship) to +1 (perfect positive relationship).",
        "The diagonal always shows 1.00 because every column is perfectly correlated with itself — this is mathematically expected and not a data issue.",
        f"The strongest relationship detected in your dataset is between {best_pair[0]} and {best_pair[1]}, with r = {best_pair[2]:.3f}, which represents a {strength} {direction} association.",
        "Dark purple cells indicate weak or no linear relationship between those two variables.",
        "Bright yellow or cream-colored cells signal strong co-movement — when one variable increases, the other tends to increase (or decrease for negative) proportionally.",
        "Use this chart to quickly identify which pairs of variables are most statistically related before building predictive models or running deeper analysis.",
    ]
    return "\n".join(f"- {line}" for line in lines)


def _trend_explanation(pipeline_result: dict) -> str:
    primary_metric = pipeline_result.get("primary_metric", "the selected metric")
    time_col = pipeline_result.get("time_col", "time")
    forecast = pipeline_result.get("forecast_results", {})
    active_unit = pipeline_result.get("active_unit", "")

    unit_note = f" in {active_unit}" if active_unit else ""

    forecast_note = ""
    if forecast and forecast.get("best_method"):
        method_data = forecast.get("methods", {}).get(forecast["best_method"], {})
        label = method_data.get("label", "")
        vals = method_data.get("forecast", [])
        if vals:
            direction = "upward" if vals[-1] > vals[0] else "downward"
            forecast_note = (
                f"The forecasting model used is {label}, which projects a {direction} trajectory "
                f"over the next {len(vals)} steps{unit_note}."
            )

    lines = [
        f"This chart plots {primary_metric}{unit_note} over {time_col}, showing how the metric changes across time periods.",
        "Each data point represents the mean value for that time period after grouping all rows that share the same timestamp — this prevents visual noise from repeated measurements.",
        "The solid purple line traces the actual observed trend, and the purple shaded area beneath it highlights the cumulative magnitude relative to zero.",
        "The dashed amber line is an OLS (Ordinary Least Squares) regression trend fitted across all time points, showing the overall linear direction of the data.",
        "The amber shaded band around the trend line is a 95% confidence interval for the mean response, computed using the formula: fitted value plus or minus t-critical times the standard error of the fit. It widens toward the edges because predictions are less certain farther from the center of the data.",
        "This confidence band does NOT mean that 95% of individual data points fall inside it — it means we are 95% confident the true population mean response line lies within that band.",
    ]

    if forecast_note:
        lines.append(forecast_note)

    return "\n".join(f"- {line}" for line in lines)


def _bar_explanation(pipeline_result: dict) -> str:
    primary_metric = pipeline_result.get("primary_metric", "the metric")
    if primary_metric == "__row_count__":
        primary_metric = "record count"
    cat_col = pipeline_result.get("categorical_col", "the category")
    active_unit = pipeline_result.get("active_unit", "")
    descriptive_stats = pipeline_result.get("descriptive_stats", {})

    unit_note = f" ({active_unit})" if active_unit else ""

    agg_used = "mean"
    skew_note = ""
    if primary_metric in descriptive_stats:
        skew = descriptive_stats[primary_metric].get("skewness", 0.0)
        agg_used = "median" if abs(skew) > 1.0 else "mean"
        if abs(skew) > 1.0:
            skew_note = (
                f"Because the skewness of {primary_metric} is {skew:.2f}, which is considered highly skewed, "
                f"bars represent the median value per group rather than the mean. "
                f"The median is more robust to extreme outliers and gives a better picture of the typical value in each group."
            )
        else:
            skew_note = (
                f"The skewness of {primary_metric} is {skew:.2f}, which is approximately symmetric, "
                f"so bars represent the mean value per group. "
                f"The mean is appropriate here because the distribution is not heavily distorted by outliers."
            )
    metric_display = (
        "record count"
        if pipeline_result.get("primary_metric") == "__row_count__"
        else primary_metric
    )
    lines = [
        f"Each bar in this chart shows the {metric_display}{unit_note} for a distinct value of {cat_col}.",
        f"Bars are sorted from highest to lowest so the top-performing groups appear on the left, making it easy to rank categories at a glance.",
        "If your dataset had more than 20 unique categories, only the top 20 by row frequency are shown to prevent label overcrowding and keep the chart readable.",
        "The color alternates across bars purely for visual separation — it does not encode any additional data dimension.",
        skew_note if skew_note else None,
        "Use this chart to quickly compare which groups or categories perform best or worst on the selected metric and to identify outlier groups that deviate significantly from the overall average.",
    ]

    return "\n".join(f"- {line}" for line in lines if line)


def render_charts_layout():
    st.markdown(
        """
<style>
@media (max-width: 700px) {
    .main-header { font-size: 1.4rem !important; margin-top: 0rem !important; }
    img { width: 100% !important; height: auto !important; }
}
.chart-skip-box {
    background: #12131e;
    border-left: 3px solid #6366f1;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 8px 0 20px 0;
    color: #9ca3af;
    font-size: 0.92rem;
    line-height: 1.6;
}
.chart-explain-box {
    background: #0d0e15;
    border-left: 3px solid #a855f7;
    border-radius: 8px;
    padding: 14px 18px;
    margin: 18px 0 8px 0;
    color: #d1d5db;
    font-size: 0.88rem;
    line-height: 1.65;
}
</style>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="main-header"> PIPELINE GRAPHICAL INTERFACE</div>',
        unsafe_allow_html=True,
    )

    charts_canvas = """
    <style>
        html, body { margin:0; padding:0; overflow:hidden; }
    </style>
    <div id="charts-container" style="width:100%;height:200px;border-radius:16px;overflow:hidden;background:linear-gradient(135deg,#0d0e15 0%,#1a1c29 100%);"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('charts-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const barGroup = new THREE.Group();
        const heights = [1.2, 2.4, 1.8, 3.2, 2.0, 2.8, 1.5, 3.6, 2.2, 1.9];
        const colors  = [0x6366f1, 0xa855f7, 0xec4899, 0x6366f1, 0xa855f7, 0xec4899, 0x6366f1, 0xa855f7, 0xec4899, 0x6366f1];

        heights.forEach((h, i) => {
            const geo = new THREE.BoxGeometry(0.35, h, 0.35);
            const mat = new THREE.MeshPhongMaterial({ color: colors[i], emissive: colors[i], emissiveIntensity: 0.3, transparent: true, opacity: 0.85 });
            const bar = new THREE.Mesh(geo, mat);
            bar.position.set(i * 0.7 - 3.15, h / 2 - 2, 0);
            barGroup.add(bar);

            const capGeo = new THREE.SphereGeometry(0.2, 8, 8);
            const capMat = new THREE.MeshPhongMaterial({ color: colors[i], emissive: colors[i], emissiveIntensity: 0.8 });
            const cap = new THREE.Mesh(capGeo, capMat);
            cap.position.set(i * 0.7 - 3.15, h - 2 + 0.1, 0);
            barGroup.add(cap);
        });
        scene.add(barGroup);

        const gridHelper = new THREE.GridHelper(10, 10, 0x1f293d, 0x1f293d);
        gridHelper.position.y = -2;
        scene.add(gridHelper);

        const particleCount = 250;
        const particleGeo = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colorsArray = new Float32Array(particleCount * 3);
        const velocities = [];

        const palette = [
            new THREE.Color(0x6366f1),
            new THREE.Color(0xec4899),
            new THREE.Color(0xa855f7)
        ];

        for (let i = 0; i < particleCount; i++) {
            positions[i * 3] = (Math.random() - 0.5) * 45;
            positions[i * 3 + 1] = (Math.random() - 0.5) * 18;
            positions[i * 3 + 2] = (Math.random() - 0.5) * 12;

            velocities.push({
                x: (Math.random() - 0.5) * 0.02,
                y: (Math.random() - 0.5) * 0.02,
                z: (Math.random() - 0.5) * 0.02
            });

            const pickedColor = palette[Math.floor(Math.random() * palette.length)];
            colorsArray[i * 3] = pickedColor.r;
            colorsArray[i * 3 + 1] = pickedColor.g;
            colorsArray[i * 3 + 2] = pickedColor.b;
        }

        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        particleGeo.setAttribute('color', new THREE.BufferAttribute(colorsArray, 3));

        const pMaterial = new THREE.PointsMaterial({
            size: 0.16,
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending
        });

        const particles = new THREE.Points(particleGeo, pMaterial);
        scene.add(particles);

        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const pl = new THREE.PointLight(0xa855f7, 4, 30); pl.position.set(0, 5, 5); scene.add(pl);
        const pl2 = new THREE.PointLight(0xec4899, 3, 20); pl2.position.set(-5, 3, 3); scene.add(pl2);

        camera.position.set(0, 1.5, 7);
        camera.lookAt(0, 0, 0);

        let isHovered = false;
        container.addEventListener('mouseenter', () => isHovered = true);
        container.addEventListener('mouseleave', () => isHovered = false);

        let t = 0;
        function animate() {
            requestAnimationFrame(animate);
            t += 0.01;
            const s = isHovered ? 6 : 1;
            barGroup.rotation.y = Math.sin(t * 1.2 * s) * 0.6;
            const positionsArray = particles.geometry.attributes.position.array;
            for (let i = 0; i < particleCount; i++) {
                positionsArray[i * 3] += velocities[i].x * s;
                positionsArray[i * 3 + 1] += velocities[i].y * s;
                positionsArray[i * 3 + 2] += velocities[i].z * s;
                if (Math.abs(positionsArray[i * 3]) > 22) velocities[i].x *= -1;
                if (Math.abs(positionsArray[i * 3 + 1]) > 9) velocities[i].y *= -1;
                if (Math.abs(positionsArray[i * 3 + 2]) > 6) velocities[i].z *= -1;
            }
            particles.geometry.attributes.position.needsUpdate = true;
            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth/container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });
    </script>
    """
    st.iframe(charts_canvas, height=200)

    pipeline_result = st.session_state.get("pipeline_result")

    if not pipeline_result:
        st.info(
            "No dataset processed in this session. Upload a CSV to generate charts."
        )
        return

    st.markdown("### Correlation Heatmap")

    heatmap_path = pipeline_result.get("heatmap_path", "")
    if heatmap_path and os.path.exists(heatmap_path):
        st.image(heatmap_path, width="stretch")
        explanation_lines = _heatmap_explanation(pipeline_result)
        st.markdown(
            f'<div class="chart-explain-box"><b>What this heatmap tells you</b><br><br>'
            f'{explanation_lines.replace(chr(10), "<br>")}'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        reason = _heatmap_skip_reason(pipeline_result)
        st.markdown(
            f'<div class="chart-skip-box"><b>Correlation Heatmap not applicable for your CSV</b><br><br>'
            f"{reason}"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Trend Chart")

    trend_path = pipeline_result.get("trend_path", "")
    if trend_path and os.path.exists(trend_path):
        st.image(trend_path, width="stretch")
        explanation_lines = _trend_explanation(pipeline_result)
        st.markdown(
            f'<div class="chart-explain-box"><b>What this trend chart tells you</b><br><br>'
            f'{explanation_lines.replace(chr(10), "<br>")}'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        reason = _trend_skip_reason(pipeline_result)
        st.markdown(
            f'<div class="chart-skip-box"><b>Trend Chart not applicable for your CSV</b><br><br>'
            f"{reason}"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Bar Chart")

    bar_path = pipeline_result.get("bar_path", "")
    if bar_path and os.path.exists(bar_path):
        st.image(bar_path, width="stretch")
        explanation_lines = _bar_explanation(pipeline_result)
        st.markdown(
            f'<div class="chart-explain-box"><b>What this bar chart tells you</b><br><br>'
            f'{explanation_lines.replace(chr(10), "<br>")}'
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        reason = _bar_skip_reason(pipeline_result)
        st.markdown(
            f'<div class="chart-skip-box"><b>Bar Chart not applicable for your CSV</b><br><br>'
            f"{reason}"
            f"</div>",
            unsafe_allow_html=True,
        )
