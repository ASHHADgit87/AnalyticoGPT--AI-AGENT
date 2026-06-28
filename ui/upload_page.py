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
        
        const camera = new THREE.PerspectiveCamera(50, container.clientWidth/container.clientHeight, 0.1, 1000);
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
        
        const spacing = 7.0;

        helixGroup.position.x = 0;
        scene.add(helixGroup);

        const leftHelix = helixGroup.clone();
        leftHelix.position.x = -spacing-10;
        scene.add(leftHelix);

        const rightHelix = helixGroup.clone();
        rightHelix.position.x = spacing+10;
        scene.add(rightHelix);

        const particleCount = 250;
        const pGeometry = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
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
            colors[i * 3] = pickedColor.r;
            colors[i * 3 + 1] = pickedColor.g;
            colors[i * 3 + 2] = pickedColor.b;
        }

        pGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        pGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const pMaterial = new THREE.PointsMaterial({
            size: 0.16,
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending
        });

        const particleSystem = new THREE.Points(pGeometry, pMaterial);
        scene.add(particleSystem);

        scene.add(new THREE.AmbientLight(0xffffff, 0.6));
        const pl = new THREE.PointLight(0x6366f1, 4, 30); pl.position.set(3, 3, 3); scene.add(pl);
        const pl2 = new THREE.PointLight(0xec4899, 3, 20); pl2.position.set(-3, -3, 3); scene.add(pl2);

        camera.position.set(0, 0, 12.5);
        camera.lookAt(0, 0, 0);

        let isHovered = false;
        container.addEventListener('mouseenter', () => isHovered = true);
        container.addEventListener('mouseleave', () => isHovered = false);

        function animate() {
            requestAnimationFrame(animate);
            const s = isHovered ? 6 : 1;
            helixGroup.rotation.y += 0.008 * s;
            leftHelix.rotation.y += 0.008 * s;
            rightHelix.rotation.y += 0.008 * s;
            
            const positionsArray = particleSystem.geometry.attributes.position.array;
            for (let i = 0; i < particleCount; i++) {
                positionsArray[i * 3] += velocities[i].x * s;
                positionsArray[i * 3 + 1] += velocities[i].y * s;
                positionsArray[i * 3 + 2] += velocities[i].z * s;

                if (Math.abs(positionsArray[i * 3]) > 22) velocities[i].x *= -1;
                if (Math.abs(positionsArray[i * 3 + 1]) > 9) velocities[i].y *= -1;
                if (Math.abs(positionsArray[i * 3 + 2]) > 6) velocities[i].z *= -1;
            }
            particleSystem.geometry.attributes.position.needsUpdate = true;
            
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
        st.session_state.pop("last_uploaded_filename", None)
        st.success("Cleared saved outputs and session results.")

    pipeline_result = st.session_state.get("pipeline_result")

    if pipeline_result:
        last_filename = st.session_state.get("last_uploaded_filename", "Your dataset")
        st.success(
            f"{last_filename} processed successfully! Visit **Graphical Analytics**, **AI Deep Insights**, and **Analysis Report** pages to explore your results."
        )
        st.info(
            "A dataset is already loaded and analysed. "
            "Click **Clear saved outputs** above to remove it and upload a new file."
        )
        st.markdown("### Dataset Summary")
        st.write(pipeline_result["metadata"].dict())
        return

    uploaded_file = st.file_uploader("Upload Target Tabular Dataset", type=["csv"])

    if uploaded_file is not None:
        if not uploaded_file.name.lower().endswith(".csv"):
            st.error("Invalid file type. Please upload a .csv file.")
            return

        try:
            file_bytes = uploaded_file.read()
            pipeline = PipelineService()
            with st.spinner(
                "Processing dataset through the full pipeline...; This may take upto 3-4 mintues depending upon the datasize..."
            ):
                result = pipeline.run_full_pipeline(uploaded_file.name, file_bytes)

            st.session_state["pipeline_result"] = result
            st.session_state["last_uploaded_filename"] = uploaded_file.name
            st.rerun()

        except Exception as exc:
            st.error(f"Failed to process upload: {exc}")
