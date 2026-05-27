"""
WebGL 3D Visualization engine for Smart Judicial Case Timeline Analyzer.
Contains highly optimized, interactive Three.js component generators.
"""

import json

def get_3d_dashboard_hero():
    """Renders a spinning 3D holographic 'Judicial AI Knowledge Graph' sphere with orbital rings."""
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>3D Judicial AI Hero</title>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            body { margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: 'Space Grotesk', sans-serif; }
            #canvas-container { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; z-index: 1; }
            #hud-overlay {
                position: absolute; bottom: 20px; left: 20px; z-index: 10;
                background: rgba(6, 8, 20, 0.7); backdrop-filter: blur(8px);
                border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 8px;
                padding: 12px 18px; color: #00f0ff; pointer-events: none;
                box-shadow: 0 4px 20px rgba(0,0,0,0.5), inset 0 1px 0 rgba(0,240,255,0.1);
            }
            #hud-overlay h4 { margin: 0 0 4px 0; font-size: 13px; text-transform: uppercase; letter-spacing: 2px; color: #FFD700; }
            #hud-overlay p { margin: 0; font-size: 11px; opacity: 0.8; letter-spacing: 0.5px; }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="hud-overlay">
            <h4>Judicial AI Core</h4>
            <p id="hud-stats">Cognitive Mesh: Active &bull; Graph Nodes: 1,024</p>
        </div>
        <div id="canvas-container"></div>

        <script>
            let scene, camera, renderer, controls;
            let particleSystem, sphereMesh, rings = [];
            const container = document.getElementById('canvas-container');

            function init() {
                scene = new THREE.Scene();
                
                // Camera
                camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
                camera.position.set(0, 0, 8);

                // Renderer
                renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Orbit Controls
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.enableZoom = false;
                controls.autoRotate = true;
                controls.autoRotateSpeed = 1.0;

                // Lighting
                const ambientLight = new THREE.AmbientLight(0x0f172a, 1.5);
                scene.add(ambientLight);

                const blueLight = new THREE.PointLight(0x00f0ff, 4, 30);
                blueLight.position.set(5, 5, 5);
                scene.add(blueLight);

                const goldLight = new THREE.PointLight(0xFFD700, 3, 30);
                goldLight.position.set(-5, -5, -5);
                scene.add(goldLight);

                // Create holographic sphere mesh (wireframe)
                const sphereGeo = new THREE.IcosahedronGeometry(2, 2);
                const sphereMat = new THREE.MeshBasicMaterial({
                    color: 0x00f0ff,
                    wireframe: true,
                    transparent: true,
                    opacity: 0.15
                });
                sphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
                scene.add(sphereMesh);

                // Create sphere particles
                const particleCount = 400;
                const particleGeo = new THREE.BufferGeometry();
                const positions = new Float32Array(particleCount * 3);
                const colors = new Float32Array(particleCount * 3);

                const goldColor = new THREE.Color(0xFFD700);
                const cyanColor = new THREE.Color(0x00f0ff);

                for (let i = 0; i < particleCount; i++) {
                    // Random point on sphere
                    const u = Math.random();
                    const v = Math.random();
                    const theta = u * 2.0 * Math.PI;
                    const phi = Math.acos(2.0 * v - 1.0);
                    const r = 2.0;

                    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                    positions[i * 3 + 2] = r * Math.cos(phi);

                    // Mix gold and cyan colors
                    const mixColor = Math.random() > 0.4 ? cyanColor : goldColor;
                    colors[i * 3] = mixColor.r;
                    colors[i * 3 + 1] = mixColor.g;
                    colors[i * 3 + 2] = mixColor.b;
                }

                particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                particleGeo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

                // Create round glowing particle texture via Canvas
                const pTexture = createParticleTexture();
                const pMaterial = new THREE.PointsMaterial({
                    size: 0.18,
                    map: pTexture,
                    vertexColors: true,
                    transparent: true,
                    opacity: 0.85,
                    blending: THREE.AdditiveBlending,
                    depthWrite: false
                });

                particleSystem = new THREE.Points(particleGeo, pMaterial);
                sphereMesh.add(particleSystem);

                // Add Orbital Rings
                createRings();

                // Events
                window.addEventListener('resize', onWindowResize, false);
                document.addEventListener('mousemove', onMouseMove, false);
            }

            function createParticleTexture() {
                const canvas = document.createElement('canvas');
                canvas.width = 64;
                canvas.height = 64;
                const ctx = canvas.getContext('2d');
                
                const grad = ctx.createRadialGradient(32, 32, 0, 32, 32, 32);
                grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
                grad.addColorStop(0.2, 'rgba(0, 240, 255, 0.8)');
                grad.addColorStop(0.5, 'rgba(0, 240, 255, 0.2)');
                grad.addColorStop(1, 'rgba(0, 0, 0, 0)');
                
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, 64, 64);
                
                const texture = new THREE.CanvasTexture(canvas);
                return texture;
            }

            function createRings() {
                const ringCount = 3;
                const ringColors = [0x00f0ff, 0xFFD700, 0xff007f];
                const ringRadii = [2.5, 2.7, 3.0];
                
                for(let i = 0; i < ringCount; i++) {
                    const segments = 120;
                    const ringGeo = new THREE.BufferGeometry();
                    const ringPos = new Float32Array((segments + 1) * 3);
                    
                    const r = ringRadii[i];
                    for(let j = 0; j <= segments; j++) {
                        const theta = (j / segments) * Math.PI * 2;
                        ringPos[j*3] = r * Math.cos(theta);
                        ringPos[j*3+1] = 0;
                        ringPos[j*3+2] = r * Math.sin(theta);
                    }
                    
                    ringGeo.setAttribute('position', new THREE.BufferAttribute(ringPos, 3));
                    const ringMat = new THREE.LineBasicMaterial({
                        color: ringColors[i],
                        transparent: true,
                        opacity: 0.4
                    });
                    
                    const ring = new THREE.Line(ringGeo, ringMat);
                    // Rotate rings differently
                    if (i === 0) ring.rotation.x = Math.PI / 4;
                    if (i === 1) ring.rotation.z = Math.PI / 3;
                    if (i === 2) ring.rotation.x = -Math.PI / 6;
                    
                    scene.add(ring);
                    rings.push(ring);
                }
            }

            function onWindowResize() {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }

            let mouseX = 0, mouseY = 0;
            function onMouseMove(event) {
                mouseX = (event.clientX - window.innerWidth / 2) / 100;
                mouseY = (event.clientY - window.innerHeight / 2) / 100;
            }

            function animate() {
                requestAnimationFrame(animate);

                controls.update();

                // Interactive rotation sway
                sphereMesh.rotation.y += 0.003;
                sphereMesh.rotation.x += 0.001;

                // Subtle background camera mouse reactive drift
                camera.position.x += (mouseX - camera.position.x) * 0.05;
                camera.position.y += (-mouseY - camera.position.y) * 0.05;
                camera.lookAt(scene.position);

                // Rotate rings dynamically
                rings.forEach((ring, idx) => {
                    ring.rotation.y += 0.005 * (idx + 1) * (idx % 2 === 0 ? 1 : -1);
                });

                renderer.render(scene, camera);
            }

            init();
            animate();
        </script>
    </body>
    </html>
    """
    return html_code


def get_3d_bar_chart(labels, values, title, height=350):
    """
    Renders an extremely premium 3D WebGL bar chart using Three.js.
    Bars are volumetric, floating, semi-transparent glass blocks with neon wireframe overlays.
    """
    if not labels:
        labels = ["No Data"]
        values = [0]
    
    color_palette = [0x00f0ff, 0xFFD700, 0xff007f, 0x00ff66, 0x8b5cf6, 0x3b82f6]
    mapped_colors = [color_palette[i % len(color_palette)] for i in range(len(labels))]

    chart_data = json.dumps([
        {"label": str(lbl), "value": float(val), "color": mapped_colors[i]}
        for i, (lbl, val) in enumerate(zip(labels, values))
    ])

    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>3D Volumetric Bar Chart</title>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            body { margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: 'Space Grotesk', sans-serif; color: #fff; }
            #chart-container { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; z-index: 1; }
            
            /* Glassmorphism HUD tooltip */
            #hud-tooltip {
                position: absolute; z-index: 10; pointer-events: none; opacity: 0;
                background: rgba(6, 8, 20, 0.85); backdrop-filter: blur(12px);
                border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 12px;
                padding: 10px 14px; min-width: 120px; transition: opacity 0.2s cubic-bezier(0.4,0,0.2,1);
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(0, 240, 255, 0.15), inset 0 1px 0 rgba(255,255,255,0.1);
            }
            .tooltip-label { font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 2px; }
            .tooltip-value { font-size: 18px; font-weight: 700; color: #00f0ff; display: flex; align-items: baseline; gap: 4px; }
            .tooltip-percent { font-size: 11px; font-weight: 400; color: #FFD700; }
            
            /* Header titles for internal sandboxing */
            #chart-title {
                position: absolute; top: 12px; left: 16px; z-index: 5;
                font-size: 12px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600;
                color: #e2e8f0; text-shadow: 0 2px 10px rgba(0,0,0,0.5);
                display: flex; align-items: center; gap: 8px;
            }
            #chart-title::before {
                content: ''; display: inline-block; width: 6px; height: 6px; background: #00f0ff; border-radius: 50%;
                box-shadow: 0 0 8px #00f0ff;
            }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="chart-title">__TITLE__</div>
        <div id="hud-tooltip">
            <div class="tooltip-label" id="tt-label">Category</div>
            <div class="tooltip-value">
                <span id="tt-val">0</span>
                <span class="tooltip-percent" id="tt-pct">(0%)</span>
            </div>
        </div>
        <div id="chart-container"></div>

        <script>
            const data = __CHART_DATA__;
            const totalSum = data.reduce((sum, item) => sum + item.value, 0) || 1;

            let scene, camera, renderer, controls;
            let bars = [];
            const container = document.getElementById('chart-container');
            const tooltip = document.getElementById('hud-tooltip');
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();

            function init() {
                scene = new THREE.Scene();

                // Camera
                camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
                camera.position.set(0, 4.5, 7.5);

                // Renderer
                renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Controls
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.maxPolarAngle = Math.PI / 2.1;
                controls.minDistance = 3;
                controls.maxDistance = 15;

                // Lighting
                const ambient = new THREE.AmbientLight(0xffffff, 0.2);
                scene.add(ambient);

                const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
                dirLight.position.set(5, 12, 8);
                scene.add(dirLight);

                const pointLight = new THREE.PointLight(0x00f0ff, 2.5, 15);
                pointLight.position.set(0, 3, 2);
                scene.add(pointLight);

                // Draw Floor / Grid
                const gridHelper = new THREE.GridHelper(10, 10, 0x00f0ff, 0x0f172a);
                gridHelper.position.y = -0.5;
                gridHelper.material.transparent = true;
                gridHelper.material.opacity = 0.15;
                scene.add(gridHelper);

                // Draw 3D Bars
                const barCount = data.length;
                const spacing = 1.0;
                const startX = -((barCount - 1) * spacing) / 2;
                
                // Determine max scaling
                const maxVal = Math.max(...data.map(d => d.value)) || 1;
                const scaleFactor = 2.5 / maxVal;

                data.forEach((item, index) => {
                    const finalHeight = Math.max(item.value * scaleFactor, 0.05);
                    const geometry = new THREE.BoxGeometry(0.55, 1, 0.55);
                    
                    const material = new THREE.MeshPhysicalMaterial({
                        color: item.color,
                        transparent: true,
                        opacity: 0.65,
                        roughness: 0.2,
                        metalness: 0.1,
                        transmission: 0.6,
                        ior: 1.45,
                        thickness: 0.5,
                        depthWrite: false
                    });

                    const mesh = new THREE.Mesh(geometry, material);
                    mesh.geometry.translate(0, 0.5, 0);
                    mesh.position.set(startX + index * spacing, -0.5, 0);
                    
                    mesh.scale.set(1, 0.01, 1);
                    scene.add(mesh);

                    const wireframeGeo = new THREE.EdgesGeometry(geometry);
                    const wireframeMat = new THREE.LineBasicMaterial({
                        color: item.color,
                        transparent: true,
                        opacity: 0.7
                    });
                    const wireframe = new THREE.LineSegments(wireframeGeo, wireframeMat);
                    mesh.add(wireframe);

                    mesh.userData = {
                        label: item.label,
                        value: item.value,
                        percent: ((item.value / totalSum) * 100).toFixed(1) + '%',
                        color: item.color,
                        targetScaleY: finalHeight,
                        currentScaleY: 0.01
                    };

                    bars.push(mesh);
                });

                window.addEventListener('resize', onWindowResize, false);
                container.addEventListener('mousemove', onMouseMove, false);
            }

            function onWindowResize() {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }

            let hoveredBar = null;
            function onMouseMove(event) {
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

                tooltip.style.left = (event.clientX + 15) + 'px';
                tooltip.style.top = (event.clientY - 15) + 'px';
            }

            function animate() {
                requestAnimationFrame(animate);

                bars.forEach(bar => {
                    if (bar.userData.currentScaleY < bar.userData.targetScaleY) {
                        bar.userData.currentScaleY += (bar.userData.targetScaleY - bar.userData.currentScaleY) * 0.08;
                        bar.scale.y = bar.userData.currentScaleY;
                    }
                });

                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(bars);

                if (intersects.length > 0) {
                    const intersected = intersects[0].object;

                    if (hoveredBar !== intersected) {
                        if (hoveredBar) {
                            hoveredBar.material.opacity = 0.65;
                            hoveredBar.scale.x = 1.0;
                            hoveredBar.scale.z = 1.0;
                        }

                        hoveredBar = intersected;
                        hoveredBar.material.opacity = 0.95;
                        hoveredBar.scale.x = 1.08;
                        hoveredBar.scale.z = 1.08;

                        document.getElementById('tt-label').innerText = hoveredBar.userData.label;
                        document.getElementById('tt-val').innerText = hoveredBar.userData.value;
                        document.getElementById('tt-pct').innerText = '(' + hoveredBar.userData.percent + ')';
                        document.getElementById('tt-val').style.color = '#' + hoveredBar.userData.color.toString(16).padStart(6, '0');
                        tooltip.style.borderColor = '#' + hoveredBar.userData.color.toString(16).padStart(6, '0');
                        tooltip.style.opacity = '1';
                    }
                } else {
                    if (hoveredBar) {
                        hoveredBar.material.opacity = 0.65;
                        hoveredBar.scale.x = 1.0;
                        hoveredBar.scale.z = 1.0;
                        hoveredBar = null;
                        tooltip.style.opacity = '0';
                    }
                }

                if(!controls.state === -1) {
                    scene.rotation.y += 0.0005;
                }

                controls.update();
                renderer.render(scene, camera);
            }

            init();
            animate();
        </script>
    </body>
    </html>
    """
    return html_code.replace("__TITLE__", title).replace("__CHART_DATA__", chart_data)


def get_3d_timeline_helix(events_data, title="Case Event Double Helix", height=450):
    """
    Renders an elite 3D Case Timeline Helix in WebGL space.
    """
    if not events_data:
        events_data = [{
            "event_date": "N/A",
            "event_type": "Filing",
            "title": "Initialization",
            "description": "Database timeline is ready."
        }]

    event_list = []
    colors_map = {
        "Filing": 0x3498db,
        "Notice": 0x9b59b6,
        "Hearing": 0xe67e22,
        "Arguments": 0xf39c12,
        "Evidence": 0x1abc9c,
        "Order": 0xe74c3c,
        "Judgment": 0x2ecc71,
        "Adjournment": 0x95a5a6,
        "Misc": 0x7f8c8d
    }

    for ev in events_data:
        et = ev.get("event_type", "Misc")
        color = colors_map.get(et, 0x00f0ff)
        event_list.append({
            "date": ev.get("event_date", "N/A"),
            "type": et,
            "title": ev.get("title", "Event"),
            "desc": ev.get("description", "No description available.")[:250],
            "color": color
        })

    try:
        event_list = sorted(event_list, key=lambda x: x["date"])
    except Exception:
        pass

    chart_data = json.dumps(event_list)

    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>3D Case Timeline Helix</title>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600&display=swap" rel="stylesheet">
        <style>
            body { margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: 'Space Grotesk', sans-serif; color: #fff; }
            #canvas-container { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; z-index: 1; }
            
            /* Glassmorphism holographic timeline card */
            #event-card {
                position: absolute; right: 20px; top: 20px; z-index: 10;
                width: 280px; opacity: 0; transform: translateX(30px);
                background: rgba(6, 8, 20, 0.75); backdrop-filter: blur(16px);
                border: 1px solid rgba(0, 240, 255, 0.3); border-radius: 16px;
                padding: 16px 20px; color: #e2e8f0; pointer-events: none;
                transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                box-shadow: 0 15px 45px rgba(0,0,0,0.7), 0 0 20px rgba(0, 240, 255, 0.1), inset 0 1px 0 rgba(255,255,255,0.05);
            }
            .card-active { opacity: 1 !important; transform: translateX(0) !important; }
            .evt-date { font-size: 11px; font-weight: 600; color: #FFD700; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 4px; }
            .evt-type { display: inline-block; font-size: 9px; font-weight: 700; background: rgba(0,240,255,0.1); border: 1px solid #00f0ff; color: #00f0ff; padding: 2px 8px; border-radius: 20px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; }
            .evt-title { font-size: 15px; font-weight: 600; color: #fff; line-height: 1.3; margin: 0 0 8px 0; }
            .evt-desc { font-size: 11.5px; color: #94a3b8; line-height: 1.6; margin: 0; }
            
            /* Help labels */
            #instructions {
                position: absolute; bottom: 16px; left: 50%; transform: translateX(-50%); z-index: 5;
                font-size: 10px; text-transform: uppercase; letter-spacing: 1.5px; color: #64748b;
                pointer-events: none; background: rgba(10,15,30,0.5); padding: 4px 12px; border-radius: 12px;
            }
            #chart-title {
                position: absolute; top: 12px; left: 16px; z-index: 5;
                font-size: 12px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600;
                color: #e2e8f0; display: flex; align-items: center; gap: 8px;
            }
            #chart-title::before {
                content: ''; display: inline-block; width: 6px; height: 6px; background: #FFD700; border-radius: 50%;
                box-shadow: 0 0 8px #FFD700;
            }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="chart-title">__TITLE__</div>
        <div id="event-card">
            <div class="evt-date" id="c-date">2024-01-01</div>
            <span class="evt-type" id="c-type">HEARING</span>
            <h3 class="evt-title" id="c-title">First Hearing Convened</h3>
            <p class="evt-desc" id="c-desc">Court issued notices to the state regarding the quashing of the petition.</p>
        </div>
        <div id="instructions">DRAG TO ROTATE &bull; SCROLL TO ZOOM &bull; HOVER CRYSTAL FOR DETAILS</div>
        <div id="canvas-container"></div>

        <script>
            const events = __CHART_DATA__;

            let scene, camera, renderer, controls;
            let nodes = [];
            let timelineTrack, splineTrack;
            const container = document.getElementById('canvas-container');
            const card = document.getElementById('event-card');
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();

            function init() {
                scene = new THREE.Scene();

                // Camera
                camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
                camera.position.set(0, 0, 9);

                // Renderer
                renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Controls
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.minDistance = 3;
                controls.maxDistance = 15;

                // Lighting
                const ambient = new THREE.AmbientLight(0xffffff, 0.3);
                scene.add(ambient);

                const dir1 = new THREE.DirectionalLight(0x00f0ff, 1.5);
                dir1.position.set(5, 5, 5);
                scene.add(dir1);

                const dir2 = new THREE.DirectionalLight(0xFFD700, 1.2);
                dir2.position.set(-5, -5, -5);
                scene.add(dir2);

                const curvePoints = [];
                const nodeCount = events.length;
                const helixHeight = 3.5;
                const turns = nodeCount > 5 ? 1.5 : 1.0;
                
                for(let i = 0; i < 150; i++) {
                    const t = i / 149;
                    const angle = t * Math.PI * 2 * turns;
                    const radius = 1.3;
                    
                    const x = radius * Math.cos(angle);
                    const y = (t * helixHeight) - (helixHeight / 2);
                    const z = radius * Math.sin(angle);
                    curvePoints.push(new THREE.Vector3(x, y, z));
                }

                const spline = new THREE.CatmullRomCurve3(curvePoints);
                const splineGeo = new THREE.BufferGeometry().setFromPoints(spline.getPoints(200));
                
                const splineMat = new THREE.LineBasicMaterial({
                    color: 0x64748b,
                    transparent: true,
                    opacity: 0.25
                });
                splineTrack = new THREE.Line(splineGeo, splineMat);
                scene.add(splineTrack);

                events.forEach((ev, idx) => {
                    const t = idx / (nodeCount - 1 || 1) * 0.95 + 0.02; 
                    const pos = spline.getPointAt(t);

                    const geo = new THREE.OctahedronGeometry(0.18, 0);
                    const mat = new THREE.MeshPhysicalMaterial({
                        color: ev.color,
                        transparent: true,
                        opacity: 0.8,
                        roughness: 0.1,
                        metalness: 0.9,
                        emissive: ev.color,
                        emissiveIntensity: 0.25,
                        transmission: 0.8,
                        ior: 2.0
                    });

                    const crystal = new THREE.Mesh(geo, mat);
                    crystal.position.copy(pos);
                    scene.add(crystal);

                    const edges = new THREE.EdgesGeometry(geo);
                    const lineMat = new THREE.LineBasicMaterial({
                        color: ev.color,
                        transparent: true,
                        opacity: 0.9
                    });
                    const cage = new THREE.LineSegments(edges, lineMat);
                    crystal.add(cage);

                    const ringGeo = new THREE.RingGeometry(0.25, 0.27, 32);
                    const ringMat = new THREE.MeshBasicMaterial({
                        color: ev.color,
                        side: THREE.DoubleSide,
                        transparent: true,
                        opacity: 0.35
                    });
                    const ring = new THREE.Mesh(ringGeo, ringMat);
                    ring.rotation.x = Math.PI / 2.5;
                    crystal.add(ring);

                    crystal.userData = {
                        date: ev.date,
                        type: ev.type,
                        title: ev.title,
                        desc: ev.desc,
                        color: '#' + ev.color.toString(16).padStart(6, '0'),
                        angleOffset: Math.random() * Math.PI,
                        origY: pos.y,
                        ring: ring
                    };

                    nodes.push(crystal);
                });

                const particleCount = 150;
                const particleGeo = new THREE.BufferGeometry();
                const positions = new Float32Array(particleCount * 3);

                for (let i = 0; i < particleCount; i++) {
                    positions[i * 3] = (Math.random() - 0.5) * 15;
                    positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
                    positions[i * 3 + 2] = (Math.random() - 0.5) * 8 - 5;
                }

                particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                const pMat = new THREE.PointsMaterial({
                    size: 0.06,
                    color: 0x00f0ff,
                    transparent: true,
                    opacity: 0.25
                });
                const particles = new THREE.Points(particleGeo, pMat);
                scene.add(particles);

                window.addEventListener('resize', onWindowResize, false);
                container.addEventListener('mousemove', onMouseMove, false);
            }

            function onWindowResize() {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }

            function onMouseMove(event) {
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
            }

            let activeNode = null;
            function animate() {
                requestAnimationFrame(animate);

                const time = Date.now() * 0.001;

                nodes.forEach(node => {
                    node.rotation.y += 0.01;
                    node.position.y = node.userData.origY + Math.sin(time * 1.5 + node.userData.angleOffset) * 0.04;
                    node.userData.ring.rotation.z += 0.02;
                });

                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(nodes);

                if (intersects.length > 0) {
                    const hit = intersects[0].object;
                    
                    if (activeNode !== hit) {
                        if (activeNode) {
                            activeNode.scale.set(1.0, 1.0, 1.0);
                            activeNode.material.emissiveIntensity = 0.25;
                        }
                        
                        activeNode = hit;
                        activeNode.scale.set(1.4, 1.4, 1.4);
                        activeNode.material.emissiveIntensity = 1.0;

                        document.getElementById('c-date').innerText = activeNode.userData.date;
                        document.getElementById('c-type').innerText = activeNode.userData.type;
                        document.getElementById('c-title').innerText = activeNode.userData.title;
                        document.getElementById('c-desc').innerText = activeNode.userData.desc;
                        
                        document.getElementById('c-date').style.color = activeNode.userData.color;
                        document.getElementById('c-type').style.color = activeNode.userData.color;
                        document.getElementById('c-type').style.borderColor = activeNode.userData.color;
                        card.style.borderColor = activeNode.userData.color;
                        card.style.boxShadow = '0 15px 45px rgba(0,0,0,0.6), 0 0 25px ' + activeNode.userData.color + '33';
                        card.classList.add('card-active');
                    }
                } else {
                    if (activeNode) {
                        activeNode.scale.set(1.0, 1.0, 1.0);
                        activeNode.material.emissiveIntensity = 0.25;
                        activeNode = null;
                        card.classList.remove('card-active');
                    }
                }

                scene.rotation.y = Math.sin(time * 0.1) * 0.15;

                controls.update();
                renderer.render(scene, camera);
            }

            init();
            animate();
        </script>
    </body>
    </html>
    """
    return html_code.replace("__TITLE__", title).replace("__CHART_DATA__", chart_data)


def get_3d_pie_chart(labels, values, title, height=350):
    """
    Renders an elegant 3D holographic ring/torus chart in WebGL.
    """
    if not labels:
        labels = ["No Data"]
        values = [0]

    color_palette = [0x00f0ff, 0xFFD700, 0xff007f, 0x00ff66, 0x8b5cf6, 0x3b82f6]
    mapped_colors = [color_palette[i % len(color_palette)] for i in range(len(labels))]

    total = sum(values) or 1
    segments = []
    
    curr_angle = 0
    for lbl, val, col in zip(labels, values, mapped_colors):
        pct = val / total
        sweep = pct * 6.283185307179586
        segments.append({
            "label": str(lbl),
            "value": float(val),
            "percent": f"{pct*100:.1f}%",
            "start": curr_angle,
            "sweep": sweep,
            "color": col
        })
        curr_angle += sweep

    chart_data = json.dumps(segments)

    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>3D Segmented Donut Chart</title>
        <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;600&display=swap" rel="stylesheet">
        <style>
            body { margin: 0; padding: 0; background: transparent; overflow: hidden; font-family: 'Space Grotesk', sans-serif; color: #fff; }
            #chart-container { width: 100vw; height: 100vh; position: absolute; top: 0; left: 0; z-index: 1; }
            
            #hud-tooltip {
                position: absolute; z-index: 10; pointer-events: none; opacity: 0;
                background: rgba(6, 8, 20, 0.85); backdrop-filter: blur(12px);
                border: 1px solid rgba(0, 240, 255, 0.4); border-radius: 12px;
                padding: 10px 14px; min-width: 120px; transition: opacity 0.2s;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), 0 0 15px rgba(0, 240, 255, 0.15), inset 0 1px 0 rgba(255,255,255,0.1);
            }
            .tooltip-label { font-size: 11px; text-transform: uppercase; color: #94a3b8; letter-spacing: 1.5px; margin-bottom: 2px; }
            .tooltip-value { font-size: 18px; font-weight: 700; color: #00f0ff; display: flex; align-items: baseline; gap: 4px; }
            .tooltip-percent { font-size: 11px; font-weight: 400; color: #FFD700; }
            
            #chart-title {
                position: absolute; top: 12px; left: 16px; z-index: 5;
                font-size: 12px; text-transform: uppercase; letter-spacing: 2px; font-weight: 600;
                color: #e2e8f0; display: flex; align-items: center; gap: 8px;
            }
            #chart-title::before {
                content: ''; display: inline-block; width: 6px; height: 6px; background: #ff007f; border-radius: 50%;
                box-shadow: 0 0 8px #ff007f;
            }
        </style>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    </head>
    <body>
        <div id="chart-title">__TITLE__</div>
        <div id="hud-tooltip">
            <div class="tooltip-label" id="tt-label">Class</div>
            <div class="tooltip-value">
                <span id="tt-val">0</span>
                <span class="tooltip-percent" id="tt-pct">(0%)</span>
            </div>
        </div>
        <div id="chart-container"></div>

        <script>
            const segments = __CHART_DATA__;

            let scene, camera, renderer, controls;
            let groupMesh;
            let segmentMeshes = [];
            const container = document.getElementById('chart-container');
            const tooltip = document.getElementById('hud-tooltip');
            const raycaster = new THREE.Raycaster();
            const mouse = new THREE.Vector2();

            function init() {
                scene = new THREE.Scene();

                // Camera
                camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 100);
                camera.position.set(0, 3.2, 5.2);

                // Renderer
                renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(window.innerWidth, window.innerHeight);
                renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
                container.appendChild(renderer.domElement);

                // Controls
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;
                controls.enableZoom = false;

                // Lighting
                const ambient = new THREE.AmbientLight(0xffffff, 0.35);
                scene.add(ambient);

                const point1 = new THREE.PointLight(0x00f0ff, 2.5, 10);
                point1.position.set(3, 5, 2);
                scene.add(point1);

                const point2 = new THREE.PointLight(0xff007f, 2, 10);
                point2.position.set(-3, -5, -2);
                scene.add(point2);

                // Volumetric Torus Segments Group
                groupMesh = new THREE.Group();
                groupMesh.rotation.x = -Math.PI / 4;
                scene.add(groupMesh);

                segments.forEach(seg => {
                    const geometry = new THREE.TorusGeometry(1.0, 0.24, 20, 60, seg.sweep);
                    
                    const material = new THREE.MeshPhysicalMaterial({
                        color: seg.color,
                        transparent: true,
                        opacity: 0.65,
                        roughness: 0.25,
                        metalness: 0.1,
                        transmission: 0.5,
                        ior: 1.5,
                        depthWrite: false
                    });

                    const slice = new THREE.Mesh(geometry, material);
                    slice.rotation.z = seg.start;
                    groupMesh.add(slice);

                    const edgesGeo = new THREE.EdgesGeometry(geometry);
                    const lineMat = new THREE.LineBasicMaterial({
                        color: seg.color,
                        transparent: true,
                        opacity: 0.7
                    });
                    const wireframe = new THREE.LineSegments(edgesGeo, lineMat);
                    slice.add(wireframe);

                    slice.userData = {
                        label: seg.label,
                        value: seg.value,
                        percent: seg.percent,
                        color: seg.color,
                        originalScale: 1.0,
                        currentScale: 0.01,
                        targetScale: 1.0
                    };

                    slice.scale.set(0.01, 0.01, 0.01);
                    segmentMeshes.push(slice);
                });

                const ringGeo = new THREE.RingGeometry(1.4, 1.42, 64);
                const ringMat = new THREE.MeshBasicMaterial({
                    color: 0x00f0ff,
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.15
                });
                const outerRing = new THREE.Mesh(ringGeo, ringMat);
                outerRing.rotation.x = 0;
                groupMesh.add(outerRing);

                window.addEventListener('resize', onWindowResize, false);
                container.addEventListener('mousemove', onMouseMove, false);
            }

            function onWindowResize() {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }

            function onMouseMove(event) {
                const rect = renderer.domElement.getBoundingClientRect();
                mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
                mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

                tooltip.style.left = (event.clientX + 15) + 'px';
                tooltip.style.top = (event.clientY - 15) + 'px';
            }

            let hoveredSlice = null;
            function animate() {
                requestAnimationFrame(animate);

                segmentMeshes.forEach(mesh => {
                    if (mesh.userData.currentScale < mesh.userData.targetScale) {
                        mesh.userData.currentScale += (mesh.userData.targetScale - mesh.userData.currentScale) * 0.08;
                        mesh.scale.set(mesh.userData.currentScale, mesh.userData.currentScale, mesh.userData.currentScale);
                    }
                });

                raycaster.setFromCamera(mouse, camera);
                const intersects = raycaster.intersectObjects(segmentMeshes);

                if (intersects.length > 0) {
                    const intersected = intersects[0].object;

                    if (hoveredSlice !== intersected) {
                        if (hoveredSlice) {
                            hoveredSlice.userData.targetScale = 1.0;
                            hoveredSlice.material.opacity = 0.65;
                        }

                        hoveredSlice = intersected;
                        hoveredSlice.userData.targetScale = 1.12;
                        hoveredSlice.material.opacity = 0.95;

                        document.getElementById('tt-label').innerText = hoveredSlice.userData.label;
                        document.getElementById('tt-val').innerText = hoveredSlice.userData.value;
                        document.getElementById('tt-pct').innerText = '(' + hoveredSlice.userData.percent + ')';
                        document.getElementById('tt-val').style.color = '#' + hoveredSlice.userData.color.toString(16).padStart(6, '0');
                        tooltip.style.borderColor = '#' + hoveredSlice.userData.color.toString(16).padStart(6, '0');
                        tooltip.style.opacity = '1';
                    }
                } else {
                    if (hoveredSlice) {
                        hoveredSlice.userData.targetScale = 1.0;
                        hoveredSlice.material.opacity = 0.65;
                        hoveredSlice = null;
                        tooltip.style.opacity = '0';
                    }
                }

                groupMesh.rotation.z += 0.003;

                controls.update();
                renderer.render(scene, camera);
            }

            init();
            animate();
        </script>
    </body>
    </html>
    """
    return html_code.replace("__TITLE__", title).replace("__CHART_DATA__", chart_data)
