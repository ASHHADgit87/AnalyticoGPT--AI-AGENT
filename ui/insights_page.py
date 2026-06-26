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

        const dataCoreGroup = new THREE.Group();
        
        const tierGeo1 = new THREE.CylinderGeometry(1.2, 1.2, 0.25, 6, 1, false);
        const tierMat1 = new THREE.MeshPhongMaterial({ color: 0x6366f1, emissive: 0x1e1b4b, wireframe: true });
        const tier1 = new THREE.Mesh(tierGeo1, tierMat1);
        tier1.position.y = 0.7;
        dataCoreGroup.add(tier1);

        const tierGeo2 = new THREE.CylinderGeometry(1.4, 1.4, 0.25, 8, 1, false);
        const tierMat2 = new THREE.MeshPhongMaterial({ color: 0xa855f7, emissive: 0x4c1d95, wireframe: true });
        const tier2 = new THREE.Mesh(tierGeo2, tierMat2);
        tier2.position.y = 0;
        dataCoreGroup.add(tier2);

        const tierGeo3 = new THREE.CylinderGeometry(1.2, 1.2, 0.25, 6, 1, false);
        const tierMat3 = new THREE.MeshPhongMaterial({ color: 0xec4899, emissive: 0x831843, wireframe: true });
        const tier3 = new THREE.Mesh(tierGeo3, tierMat3);
        tier3.position.y = -0.7;
        dataCoreGroup.add(tier3);

        scene.add(dataCoreGroup);

        const ringGroup = new THREE.Group();
        for (let r = 0; r < 3; r++) {
            const ring = new THREE.Mesh(
                new THREE.TorusGeometry(2.3 + r * 0.3, 0.02, 6, 60),
                new THREE.MeshPhongMaterial({ color: r === 0 ? 0x6366f1 : r === 1 ? 0xa855f7 : 0xec4899, emissive: 0x1e1b4b, transparent: true, opacity: 0.4 })
            );
            ring.rotation.x = Math.PI / (2 + r);
            ring.rotation.z = r * 0.5;
            ringGroup.add(ring);
        }
        scene.add(ringGroup);

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
        const pl = new THREE.PointLight(0x6366f1, 4, 25); pl.position.set(3, 4, 4); scene.add(pl);
        const pl2 = new THREE.PointLight(0xec4899, 3, 20); pl2.position.set(-3, -2, 3); scene.add(pl2);

        camera.position.set(0, 0.5, 5.5);
        camera.lookAt(0, 0, 0);

        let isHovered = false;
        container.addEventListener('mouseenter', () => isHovered = true);
        container.addEventListener('mouseleave', () => isHovered = false);

        let t = 0;
        function animate() {
            requestAnimationFrame(animate);
            t += 0.008;
            const s = isHovered ? 6 : 1;
            
            tier1.rotation.y += 0.01 * s;
            tier2.rotation.y -= 0.015 * s;
            tier3.rotation.y += 0.008 * s;
            
            dataCoreGroup.rotation.x = Math.sin(t * 0.4) * 0.2;
            dataCoreGroup.rotation.z = Math.cos(t * 0.3) * 0.1;
            
            ringGroup.rotation.y += 0.005 * s;
            ringGroup.rotation.x += 0.003 * s;

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
