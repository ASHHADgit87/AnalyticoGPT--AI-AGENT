import streamlit as st
import streamlit.components.v1 as components


def render_insights_layout():
    st.markdown(
        '<div class="main-header"> CRITICAL AI NARRATIVE INSIGHTS</div>',
        unsafe_allow_html=True,
    )

    insights_canvas = """
    <div id="insights-container" style="width:100%;height:200px;border-radius:16px;overflow:hidden;background:linear-gradient(135deg,#0d0e15 0%,#1a1c29 100%);"></div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        const container = document.getElementById('insights-container');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(60, container.clientWidth/container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        const nodeGroup = new THREE.Group();
        const nodeMat = new THREE.MeshPhongMaterial({ color: 0xa855f7, emissive: 0x4c1d95 });
        const lineMat = new THREE.LineBasicMaterial({ color: 0x6366f1, transparent: true, opacity: 0.4 });

        const layers = [[[-2, 1], [-2, 0], [-2, -1]], [[-0.5, 1.5], [-0.5, 0.5], [-0.5, -0.5], [-0.5, -1.5]], [[1, 1], [1, 0], [1, -1]], [[2.5, 0.5], [2.5, -0.5]]];
        const nodePositions = [];

        layers.forEach((layer, li) => {
            layer.forEach(([x, y]) => {
                const node = new THREE.Mesh(new THREE.SphereGeometry(0.18, 12, 12), nodeMat.clone());
                node.position.set(x, y, (Math.random() - 0.5) * 0.5);
                nodeGroup.add(node);
                nodePositions.push({ x, y, z: node.position.z, layer: li });
            });
        });

        nodePositions.forEach(a => {
            nodePositions.forEach(b => {
                if (b.layer === a.layer + 1) {
                    const pts = [new THREE.Vector3(a.x, a.y, a.z), new THREE.Vector3(b.x, b.y, b.z)];
                    nodeGroup.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), lineMat));
                }
            });
        });
        scene.add(nodeGroup);

        const pulseGeo = new THREE.SphereGeometry(0.08, 8, 8);
        const pulseMat = new THREE.MeshPhongMaterial({ color: 0xec4899, emissive: 0xec4899, emissiveIntensity: 1 });
        const pulses = [];
        for (let i = 0; i < 6; i++) {
            const p = new THREE.Mesh(pulseGeo, pulseMat);
            pulses.push({ mesh: p, t: Math.random() });
            scene.add(p);
        }

        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const pl = new THREE.PointLight(0xa855f7, 4, 20); pl.position.set(0, 3, 3); scene.add(pl);
        const pl2 = new THREE.PointLight(0xec4899, 3, 15); pl2.position.set(2, -2, 2); scene.add(pl2);

        camera.position.set(0, 0, 6);

        const path = [[-2,0,0],[-0.5,0.8,0],[1,0,0],[2.5,0.3,0]];
        function lerpPath(progress) {
            const seg = progress * (path.length - 1);
            const idx = Math.min(Math.floor(seg), path.length - 2);
            const frac = seg - idx;
            const a = path[idx], b = path[idx + 1];
            return [a[0]+(b[0]-a[0])*frac, a[1]+(b[1]-a[1])*frac, a[2]+(b[2]-a[2])*frac];
        }

        let isHovered = false;
        container.addEventListener('mouseenter', () => isHovered = true);
        container.addEventListener('mouseleave', () => isHovered = false);

        let t = 0;
        function animate() {
            requestAnimationFrame(animate);
            t += 0.005;
            const s = isHovered ? 6 : 1;
            nodeGroup.rotation.y = Math.sin(t * 0.5 * s) * 0.2;
            pulses.forEach((p, i) => {
                p.t = (p.t + (0.008 + i * 0.002) * s) % 1;
                const [x, y, z] = lerpPath(p.t);
                p.mesh.position.set(x + (Math.random()-0.5)*0.05, y + (Math.random()-0.5)*0.05, z);
            });
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
    components.html(insights_canvas, height=200)

    pipeline_result = st.session_state.get("pipeline_result")
    if pipeline_result:
        insight_text = pipeline_result.get(
            "insight_text", "No narrative insights were generated."
        )
        st.markdown(insight_text)
    else:
        st.info(
            "No dataset has been uploaded yet. Upload a CSV in the Data Ingestion Engine to generate insights."
        )
