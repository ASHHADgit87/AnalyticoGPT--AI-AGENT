import streamlit as st
import streamlit.components.v1 as components


def render_dashboard_layout():
    st.markdown(
        '<div class="main-header"> AnalyticoGPT ORCHESTRATION</div>',
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
        renderer.setPixelRatio(window.devicePixelRatio);
        container.appendChild(renderer.domElement);

        const coreGeo = new THREE.IcosahedronGeometry(1.5, 1);
        const coreMat = new THREE.MeshPhongMaterial({ color: 0x6366f1, wireframe: true, emissive: 0x312e81, shininess: 200 });
        const core = new THREE.Mesh(coreGeo, coreMat);
        scene.add(core);

        const shellGeo = new THREE.IcosahedronGeometry(2.4, 1);
        const shellMat = new THREE.MeshPhongMaterial({ color: 0xa855f7, wireframe: true, emissive: 0x4c1d95, shininess: 100, opacity: 0.4, transparent: true });
        const shell = new THREE.Mesh(shellGeo, shellMat);
        scene.add(shell);

        const torusGeo = new THREE.TorusGeometry(3.2, 0.05, 8, 80);
        const torusMat = new THREE.MeshPhongMaterial({ color: 0xec4899, emissive: 0x831843 });
        const torus = new THREE.Mesh(torusGeo, torusMat);
        torus.rotation.x = Math.PI / 3;
        scene.add(torus);

        const torus2Geo = new THREE.TorusGeometry(3.2, 0.05, 8, 80);
        const torus2Mat = new THREE.MeshPhongMaterial({ color: 0x6366f1, emissive: 0x1e1b4b });
        const torus2 = new THREE.Mesh(torus2Geo, torus2Mat);
        torus2.rotation.x = Math.PI / 1.5;
        torus2.rotation.y = Math.PI / 4;
        scene.add(torus2);

        const particleCount = 250;
        const particleGeo = new THREE.BufferGeometry();
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

        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

        const particleMat = new THREE.PointsMaterial({
            size: 0.16,
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending
        });

        const particles = new THREE.Points(particleGeo, particleMat);
        scene.add(particles);

        scene.add(new THREE.AmbientLight(0xffffff, 0.5));
        const p1 = new THREE.PointLight(0xec4899, 3, 50); p1.position.set(5, 5, 5); scene.add(p1);
        const p2 = new THREE.PointLight(0x6366f1, 3, 50); p2.position.set(-5, -5, -5); scene.add(p2);
        const p3 = new THREE.PointLight(0xa855f7, 2, 30); p3.position.set(0, 8, 0); scene.add(p3);

        camera.position.z = 7;

        let isHovered = false;
        container.addEventListener('mouseenter', () => isHovered = true);
        container.addEventListener('mouseleave', () => isHovered = false);

        let t = 0;
        function animate() {
            requestAnimationFrame(animate);
            t += 0.01;
            const s = isHovered ? 6 : 1;
            
            core.rotation.x += 0.004 * s;
            core.rotation.y += 0.007 * s;
            shell.rotation.x -= 0.003 * s;
            shell.rotation.y -= 0.005 * s;
            
            torus.rotation.x += 0.003;
            torus.rotation.y += 0.0025;
            torus.rotation.z += 0.005;
            
            torus2.rotation.x -= 0.0025;
            torus2.rotation.y += 0.003;
            torus2.rotation.z -= 0.005;
            
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
            
            p1.position.x = Math.sin(t) * 6;
            p1.position.z = Math.cos(t) * 6;
            p2.position.x = Math.cos(t * 0.7) * 6;
            p2.position.z = Math.sin(t * 0.7) * 6;
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
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        st.info(
            "No dataset uploaded yet. Use the Data Ingestion Engine to upload and process a CSV."
        )
