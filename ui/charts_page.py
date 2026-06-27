import streamlit as st
import streamlit.components.v1 as components
import os


def render_charts_layout():
    st.markdown(
        """
<style>
@media (max-width: 700px) {
    .main-header { font-size: 1.4rem !important; margin-top: 0rem !important; }
    img { width: 100% !important; height: auto !important; }
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
    components.html(charts_canvas, height=200)

    pipeline_result = st.session_state.get("pipeline_result")
    if pipeline_result:
        shown = False

        if pipeline_result.get("heatmap_path") and os.path.exists(
            pipeline_result["heatmap_path"]
        ):
            st.markdown("### Correlation Heatmap")
            st.image(pipeline_result["heatmap_path"], width="stretch")
            shown = True

        if pipeline_result.get("trend_path") and os.path.exists(
            pipeline_result["trend_path"]
        ):
            st.markdown("### Trend Chart")
            st.image(pipeline_result["trend_path"], width="stretch")
            shown = True

        if pipeline_result.get("bar_path") and os.path.exists(
            pipeline_result["bar_path"]
        ):
            st.markdown("### Bar Chart")
            st.image(pipeline_result["bar_path"], width="stretch")
            shown = True

        if not shown:
            st.info("No charts were generated for the current dataset.")
    else:
        st.info(
            "No dataset processed in this session. Upload a CSV to generate charts."
        )
