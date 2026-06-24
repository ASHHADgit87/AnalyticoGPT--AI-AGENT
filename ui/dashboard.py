import streamlit as st
import streamlit.components.v1 as components


def render_dashboard_layout():
    st.markdown(
        '<div class="main-header">✨ ANALYTICOGPT ORCHESTRATION</div>',
        unsafe_allow_html=True,
    )

    threejs_canvas = """
    <div id="three-container" style="width: 100%; height: 250px; border-radius: 16px; overflow: hidden; background: linear-gradient(135deg, #0d0e15 0%, #1a1c29 100%);"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('three-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const geometry = new THREE.IcosahedronGeometry(2, 1);
        const material = new THREE.MeshPhongMaterial({
            color: 0x6366f1,
            wireframe: true,
            emissive: 0x312e81,
            shininess: 100
        });
        const mesh = new THREE.Mesh(geometry, material);
        scene.add(mesh);

        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const pointLight = new THREE.PointLight(0xec4899, 2, 50);
        pointLight.position.set(5, 5, 5);
        scene.add(pointLight);

        camera.position.z = 5;

        function animate() {
            requestAnimationFrame(animate);
            mesh.rotation.x += 0.005;
            mesh.rotation.y += 0.008;
            renderer.render(scene, camera);
        }
        animate();
        window.addEventListener('resize', () => {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
        });
    </script>
    """
    components.html(threejs_canvas, height=250)

    pipeline_result = st.session_state.get("pipeline_result")
    records_parsed = "-"
    max_correlation = "-"

    if pipeline_result:
        records_parsed = pipeline_result["metadata"].row_count
        correlation_matrix = pipeline_result.get("correlation_matrix", {})
        if correlation_matrix:
            max_correlation = max(
                abs(value)
                for row in correlation_matrix.values()
                for value in row.values()
            )
            max_correlation = f"{max_correlation:.3f}"
        else:
            max_correlation = "N/A"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f'<div class="metric-card"><h3>{records_parsed}</h3><p>Records Parsed</p></div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card"><h3>{max_correlation}</h3><p>Max Target Correlation</p></div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            '<div class="metric-card"><h3>100%</h3><p>Agent Synchronization</p></div>',
            unsafe_allow_html=True,
        )

    if not pipeline_result:
        st.info("No dataset uploaded yet. Use the Data Ingestion Engine to upload and process a CSV.")
