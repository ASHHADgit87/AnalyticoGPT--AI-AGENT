import streamlit as st
import streamlit.components.v1 as components
from services.pipeline_service import PipelineService
import os
import shutil


def render_upload_layout():
    st.markdown(
        '<div class="main-header"> DATA INGESTION ENGINE</div>',
        unsafe_allow_html=True,
    )

    ingestion_canvas = """
    <div id="ingest-container" style="width:100%;height:200px;border-radius:16px;overflow:hidden;background:linear-gradient(135deg,#0d0e15 0%,#1a1c29 100%);"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('ingest-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const helixGroup = new THREE.Group();
        const strandMat1 = new THREE.MeshPhongMaterial({ color: 0x6366f1, emissive: 0x1e1b4b });
        const strandMat2 = new THREE.MeshPhongMaterial({ color: 0xec4899, emissive: 0x831843 });
        const bridgeMat = new THREE.MeshPhongMaterial({ color: 0xa855f7, emissive: 0x4c1d95, opacity: 0.6, transparent: true });

        for (let i = 0; i < 40; i++) {
            const t = (i / 40) * Math.PI * 4;
            const x1 = Math.cos(t) * 1.5, y = (i / 40) * 8 - 4, x2 = Math.cos(t + Math.PI) * 1.5;
            const z1 = Math.sin(t) * 1.5, z2 = Math.sin(t + Math.PI) * 1.5;

            const s1 = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), strandMat1);
            s1.position.set(x1, y, z1); helixGroup.add(s1);

            const s2 = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), strandMat2);
            s2.position.set(x2, y, z2); helixGroup.add(s2);

            if (i % 4 === 0) {
                const bridgeGeo = new THREE.CylinderGeometry(0.03, 0.03, Math.sqrt((x2-x1)**2+(z2-z1)**2), 4);
                const bridge = new THREE.Mesh(bridgeGeo, bridgeMat);
                bridge.position.set((x1+x2)/2, y, (z1+z2)/2);
                bridge.rotation.z = Math.PI / 2;
                bridge.lookAt(x2, y, z2);
                helixGroup.add(bridge);
            }
        }
        scene.add(helixGroup);

        scene.add(new THREE.AmbientLight(0xffffff, 0.6));
        const pl = new THREE.PointLight(0x6366f1, 4, 30); pl.position.set(3, 3, 3); scene.add(pl);
        const pl2 = new THREE.PointLight(0xec4899, 3, 20); pl2.position.set(-3, -3, 3); scene.add(pl2);

        camera.position.set(4, 0, 6);
        camera.lookAt(0, 0, 0);

        let isHovered = false;
        container.addEventListener('mouseenter', () => isHovered = true);
        container.addEventListener('mouseleave', () => isHovered = false);

        function animate() {
            requestAnimationFrame(animate);
            const s = isHovered ? 6 : 1;
            helixGroup.rotation.y += 0.008 * s;
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
    components.html(ingestion_canvas, height=200)

    if st.button("Clear saved outputs (charts & reports)"):
        for d in ["outputs/charts", "outputs/reports", "data/cleaned"]:
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception:
                    pass
        os.makedirs("outputs/charts", exist_ok=True)
        os.makedirs("outputs/reports", exist_ok=True)
        os.makedirs("data/cleaned", exist_ok=True)
        st.session_state.pop("pipeline_result", None)
        st.success("Cleared saved outputs and session results.")

    uploaded_file = st.file_uploader("Upload Target Tabular Dataset", type=["csv"])

    if uploaded_file is not None:
        if not uploaded_file.name.lower().endswith(".csv"):
            st.error("Invalid file type. Please upload a .csv file.")
            return

        try:
            file_bytes = uploaded_file.read()
            pipeline = PipelineService()
            with st.spinner("Processing dataset through the full pipeline..."):
                result = pipeline.run_full_pipeline(uploaded_file.name, file_bytes)

            st.session_state["pipeline_result"] = result
            st.success(
                f" {uploaded_file.name} processed successfully! Visit **Graphical Analytics**, **AI Deep Insights**, and **Analysis Report** pages to explore your results."
            )

            st.markdown("### Dataset Summary")
            st.write(result["metadata"].dict())

        except Exception as exc:
            st.error(f"Failed to process upload: {exc}")
