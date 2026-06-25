import streamlit as st
import streamlit.components.v1 as components
import os


def render_reports_layout():
    st.markdown(
        '<div class="main-header"> EXECUTIVE REPORT CORES</div>',
        unsafe_allow_html=True,
    )

    reports_canvas = """
    <div id="reports-container" style="width:100%;height:200px;border-radius:16px;overflow:hidden;background:linear-gradient(135deg,#0d0e15 0%,#1a1c29 100%);"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('reports-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const docGroup = new THREE.Group();
        const pageMat = new THREE.MeshPhongMaterial({ color: 0x1e293b, emissive: 0x0f172a, transparent: true, opacity: 0.9, side: THREE.DoubleSide });
        const lineMat = new THREE.MeshPhongMaterial({ color: 0x6366f1, emissive: 0x1e1b4b });
        const accentMat = new THREE.MeshPhongMaterial({ color: 0xec4899, emissive: 0x831843 });

        for (let d = 0; d < 3; d++) {
            const page = new THREE.Mesh(new THREE.PlaneGeometry(1.4, 1.8), pageMat.clone());
            page.position.set(d * 1.8 - 1.8, 0, d * -0.3);
            page.rotation.y = (d - 1) * 0.2;
            docGroup.add(page);

            for (let l = 0; l < 5; l++) {
                const w = 0.5 + Math.random() * 0.6;
                const line = new THREE.Mesh(new THREE.PlaneGeometry(w, 0.06), l === 0 ? accentMat : lineMat);
                line.position.set(d * 1.8 - 1.8 + (w - 1.2) / 2, 0.5 - l * 0.28, d * -0.3 + 0.01);
                line.rotation.y = (d - 1) * 0.2;
                docGroup.add(line);
            }
        }
        scene.add(docGroup);

        const ringGroup = new THREE.Group();
        for (let r = 0; r < 3; r++) {
            const ring = new THREE.Mesh(
                new THREE.TorusGeometry(2.5 + r * 0.4, 0.03, 6, 60),
                new THREE.MeshPhongMaterial({ color: r === 0 ? 0x6366f1 : r === 1 ? 0xa855f7 : 0xec4899, emissive: 0x1e1b4b, transparent: true, opacity: 0.5 })
            );
            ring.rotation.x = Math.PI / (2 + r);
            ring.rotation.z = r * 0.5;
            ringGroup.add(ring);
        }
        scene.add(ringGroup);

        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const pl = new THREE.PointLight(0x6366f1, 4, 25); pl.position.set(3, 4, 4); scene.add(pl);
        const pl2 = new THREE.PointLight(0xec4899, 3, 20); pl2.position.set(-3, -2, 3); scene.add(pl2);

        camera.position.set(0, 0.5, 6);
        camera.lookAt(0, 0, 0);

        let isHovered = false;
        container.addEventListener('mouseenter', () => isHovered = true);
        container.addEventListener('mouseleave', () => isHovered = false);

        let t = 0;
        function animate() {
            requestAnimationFrame(animate);
            t += 0.008;
            const s = isHovered ? 6 : 1;
            docGroup.rotation.y = Math.sin(t * 0.4 * s) * 0.15;
            docGroup.position.y = Math.sin(t * 0.6 * s) * 0.15;
            ringGroup.rotation.y += 0.005 * s;
            ringGroup.rotation.x += 0.003 * s;
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
    components.html(reports_canvas, height=200)

    pipeline_result = st.session_state.get("pipeline_result")
    if pipeline_result and pipeline_result.get("report_path"):
        rep = pipeline_result["report_path"]
        if os.path.exists(rep):
            st.write(f" Generated Asset Reference: {os.path.basename(rep)}")
            with open(rep, "rb") as pdf_file:
                st.download_button(
                    label="Download Asset Report PDF",
                    data=pdf_file,
                    file_name=os.path.basename(rep),
                    mime="application/pdf",
                )
        else:
            st.info("The report file referenced by the session is missing on disk.")
    else:
        st.info(
            "No report generated in this session. Upload & process a dataset to generate a report."
        )
