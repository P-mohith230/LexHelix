"""
Three.js WebGL Visualization Engine for Cyberbullying App WhatsApp.
Generates highly interactive, GPU-accelerated 3D graphics (constellations, columns, helixes)
embedded via sandboxed HTML iframe channels.
"""

import json


def get_3d_dashboard_hero():
    """
    Renders the 3D Sentiment Constellation Sphere.
    Safe messages represent calm cyan/blue connecting particles;
    flagged toxicity events trigger glowing pulsing red nodes.
    """
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; overflow: hidden; background-color: #03050c; font-family: 'Space Grotesk', sans-serif; }
            #canvas-container { width: 100vw; height: 100vh; position: relative; }
            #hud-overlay {
                position: absolute; top: 15px; left: 15px;
                color: #00f0ff; font-size: 10px; font-weight: bold;
                letter-spacing: 2px; text-transform: uppercase;
                text-shadow: 0 0 10px rgba(0,240,255,0.5);
                pointer-events: none;
            }
        </style>
    </head>
    <body>
        <div id="hud-overlay">Aegis AI Shield // Sentiment Constellation</div>
        <div id="canvas-container"></div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x03050c, 0.015);

            const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 0, 80);

            const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            container.appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.rotateSpeed = 0.8;
            controls.enableZoom = false;

            // Ambient Constellation particles
            const particleCount = 280;
            const geometry = new THREE.BufferGeometry();
            const positions = new Float32Array(particleCount * 3);
            const colors = new Float32Array(particleCount * 3);

            const colorSafe = new THREE.Color('#00f0ff');
            const colorToxic = new THREE.Color('#ff007f');

            for (let i = 0; i < particleCount; i++) {
                // Sphere random layout
                const u = Math.random();
                const v = Math.random();
                const theta = u * 2.0 * Math.PI;
                const phi = Math.acos(2.0 * v - 1.0);
                const r = 30 + Math.random() * 8; // Sphere radius

                const x = r * Math.sin(phi) * Math.cos(theta);
                const y = r * Math.sin(phi) * Math.sin(theta);
                const z = r * Math.cos(phi);

                positions[i * 3] = x;
                positions[i * 3 + 1] = y;
                positions[i * 3 + 2] = z;

                // Color distribution (90% safe cyan, 10% toxic magenta/red)
                const isToxic = Math.random() > 0.88;
                const color = isToxic ? colorToxic : colorSafe;
                
                colors[i * 3] = color.r;
                colors[i * 3 + 1] = color.g;
                colors[i * 3 + 2] = color.b;
            }

            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

            // Custom canvas texture for round glowing particles
            function createCircleTexture() {
                const canvas = document.createElement('canvas');
                canvas.width = 16;
                canvas.height = 16;
                const ctx = canvas.getContext('2d');
                const grad = ctx.createRadialGradient(8, 8, 0, 8, 8, 8);
                grad.addColorStop(0, 'rgba(255, 255, 255, 1)');
                grad.addColorStop(0.3, 'rgba(255, 255, 255, 0.8)');
                grad.addColorStop(1, 'rgba(255, 255, 255, 0)');
                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, 16, 16);
                return new THREE.CanvasTexture(canvas);
            }

            const material = new THREE.PointsMaterial({
                size: 2.2,
                vertexColors: true,
                map: createCircleTexture(),
                transparent: true,
                blending: THREE.AdditiveBlending,
                depthWrite: false
            });

            const constellation = new THREE.Points(geometry, material);
            scene.add(constellation);

            // Connect nearest nodes with dynamic grid lines
            const lineGeometry = new THREE.BufferGeometry();
            const linePositions = [];
            const lineColors = [];

            const maxDistance = 14;
            for (let i = 0; i < particleCount; i++) {
                const x1 = positions[i * 3];
                const y1 = positions[i * 3 + 1];
                const z1 = positions[i * 3 + 2];

                for (let j = i + 1; j < particleCount; j++) {
                    const x2 = positions[j * 3];
                    const y2 = positions[j * 3 + 1];
                    const z2 = positions[j * 3 + 2];

                    const dist = Math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2);
                    if (dist < maxDistance) {
                        linePositions.push(x1, y1, z1, x2, y2, z2);
                        
                        // Line colors blending
                        lineColors.push(colors[i*3], colors[i*3+1], colors[i*3+2]);
                        lineColors.push(colors[j*3], colors[j*3+1], colors[j*3+2]);
                    }
                }
            }

            lineGeometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(linePositions), 3));
            lineGeometry.setAttribute('color', new THREE.BufferAttribute(new Float32Array(lineColors), 3));

            const lineMaterial = new THREE.LineBasicMaterial({
                vertexColors: true,
                transparent: true,
                opacity: 0.14,
                blending: THREE.AdditiveBlending
            });

            const gridLines = new THREE.LineSegments(lineGeometry, lineMaterial);
            scene.add(gridLines);

            // Glowing Concentric rings
            const ringGeom = new THREE.RingGeometry(38, 38.5, 64);
            const ringMat = new THREE.MeshBasicMaterial({
                color: 0x00f0ff,
                side: THREE.DoubleSide,
                transparent: true,
                opacity: 0.05,
                blending: THREE.AdditiveBlending
            });
            const outerRing = new THREE.Mesh(ringGeom, ringMat);
            outerRing.rotation.x = Math.PI / 2;
            scene.add(outerRing);

            const innerRing = new THREE.Mesh(
                new THREE.RingGeometry(25, 25.3, 64),
                new THREE.MeshBasicMaterial({
                    color: 0xff007f,
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.04,
                    blending: THREE.AdditiveBlending
                })
            );
            innerRing.rotation.y = Math.PI / 4;
            scene.add(innerRing);

            // Lighting
            const ambient = new THREE.AmbientLight(0xffffff, 0.4);
            scene.add(ambient);

            // Window resize handler
            window.addEventListener('resize', onWindowResize, false);
            function onWindowResize() {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }

            // Animation Loop
            let frame = 0;
            function animate() {
                requestAnimationFrame(animate);
                frame += 0.002;

                constellation.rotation.y = frame * 1.5;
                constellation.rotation.x = frame * 0.5;
                gridLines.rotation.y = frame * 1.5;
                gridLines.rotation.x = frame * 0.5;

                outerRing.rotation.z = -frame * 0.8;
                innerRing.rotation.x = frame * 1.2;

                controls.update();
                renderer.render(scene, camera);
            }
            animate();
        </script>
    </body>
    </html>
    """
    return html_template


def get_3d_bar_chart(labels, values, title, height=350):
    """
    Renders 3D Volumetric Moderation Columns.
    Each category (Threat, Insult, Harassment, Hate Speech, Safe) is rendered
    as a volumetric glowing glass column with its specific color.
    """
    # Color mapping for categories
    colors_map = {
        "Threat": "#ff007f",      # Crimson
        "Insult": "#ffaa00",      # Orange
        "Harassment": "#ffd700",  # Gold
        "Hate Speech": "#9b59b6",  # Purple
        "Safe": "#00f0ff",        # Cyan
    }

    # Fallback default colors
    default_colors = ["#00f0ff", "#ffaa00", "#ffd700", "#9b59b6", "#ff007f"]
    chart_colors = [colors_map.get(lbl, default_colors[i % len(default_colors)]) for i, lbl in enumerate(labels)]

    data_json = json.dumps([{"label": lbl, "val": val, "color": chart_colors[i]} for i, (lbl, val) in enumerate(zip(labels, values))])

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; overflow: hidden; background-color: #03050c; font-family: 'Space Grotesk', sans-serif; }
            #hud-title {
                position: absolute; top: 12px; left: 12px;
                color: #cbd5e1; font-size: 11px; font-weight: 600;
                letter-spacing: 1.5px; text-transform: uppercase;
                pointer-events: none; z-index: 5;
            }
        </style>
    </head>
    <body>
        <div id="hud-title">__TITLE__</div>
        <div id="canvas-container" style="width: 100vw; height: 100vh;"></div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const data = __DATA__;
            
            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x03050c, 0.02);

            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 30, 70);

            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2.1; // Restrict looking below floor
            controls.enableZoom = false;

            // Ambient and directional lighting
            const ambient = new THREE.AmbientLight(0xffffff, 0.35);
            scene.add(ambient);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.85);
            dirLight.position.set(20, 40, 20);
            scene.add(dirLight);

            // Coordinates Floor Grid
            const gridHelper = new THREE.GridHelper(80, 20, 0x00f0ff, 0x1f2937);
            gridHelper.position.y = 0;
            gridHelper.material.opacity = 0.18;
            gridHelper.material.transparent = true;
            scene.add(gridHelper);

            // Build columns
            const colWidth = 6;
            const spacing = 12;
            const startX = -((data.length - 1) * spacing) / 2;

            const columns = [];

            data.forEach((item, index) => {
                // Calculate height proportionally, handle 0 gracefully
                const valHeight = Math.max(item.val * 2, 0.8); 
                const x = startX + index * spacing;

                // Create volumetric column box mesh
                const geometry = new THREE.BoxGeometry(colWidth, valHeight, colWidth);
                
                // Frosted glowing glass material
                const material = new THREE.MeshPhysicalMaterial({
                    color: new THREE.Color(item.color),
                    transparent: true,
                    opacity: 0.65,
                    roughness: 0.15,
                    metalness: 0.1,
                    transmission: 0.5,
                    thickness: 1.5,
                    ior: 1.5,
                    side: THREE.DoubleSide
                });

                const mesh = new THREE.Mesh(geometry, material);
                mesh.position.set(x, valHeight / 2, 0);
                scene.add(mesh);
                columns.push(mesh);

                // Glowing neon wireframes
                const edges = new THREE.EdgesGeometry(geometry);
                const lineMat = new THREE.LineBasicMaterial({
                    color: new THREE.Color(item.color),
                    transparent: true,
                    opacity: 0.8,
                    blending: THREE.AdditiveBlending
                });
                const wireframe = new THREE.LineSegments(edges, lineMat);
                mesh.add(wireframe);

                // Ambient point light inside each glass column
                const pLight = new THREE.PointLight(item.color, 1.8, 15);
                pLight.position.set(0, 0, 0);
                mesh.add(pLight);
            });

            // Base platform glow
            const platformGeom = new THREE.BoxGeometry(70, 0.5, 20);
            const platformMat = new THREE.MeshBasicMaterial({
                color: 0x0b0f19,
                transparent: true,
                opacity: 0.5
            });
            const platform = new THREE.Mesh(platformGeom, platformMat);
            platform.position.set(0, -0.25, 0);
            scene.add(platform);

            // Animation Loop
            let angle = 0;
            function animate() {
                requestAnimationFrame(animate);
                angle += 0.003;

                // Slow rotation around the columns
                scene.rotation.y = Math.sin(angle) * 0.15;

                // Pulse core light intensity
                columns.forEach((col) => {
                    const light = col.children.find(child => child.isPointLight);
                    if (light) {
                        light.intensity = 1.4 + Math.sin(angle * 20) * 0.3;
                    }
                });

                controls.update();
                renderer.render(scene, camera);
            }
            animate();

            // Resize support
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        </script>
    </body>
    </html>
    """.replace("__TITLE__", title).replace("__DATA__", data_json)
    return html_template


def get_3d_timeline_helix(events_data, title="Case Event Double Helix", height=450):
    """
    Renders the 3D Message Timeline Helix.
    Dialogues are mapped along a dual-helix track.
    Safe messages are green octahedrons.
    Censored/Flagged messages are glowing red spheres/spikes.
    """
    # Restructure event details to feed safely into Javascript list
    formatted_events = []
    for i, evt in enumerate(events_data):
        # Determine classification color
        tag = evt.get("classification_tag", "Safe")
        is_toxic = evt.get("is_toxic", 0)
        is_deleted = evt.get("is_deleted", 0)
        
        color = "#00f0ff" # Safe (Cyan)
        if is_toxic or is_deleted:
            color = "#ff007f" # Flagged (Red)

        formatted_events.append({
            "id": i + 1,
            "text": evt.get("original_text", evt.get("message_text", "")),
            "sender": "Aarav" if evt.get("sender_id") == 1 else ("Priya" if evt.get("sender_id") == 2 else "Contact"),
            "color": color,
            "is_toxic": is_toxic or is_deleted,
            "tag": tag
        })

    events_json = json.dumps(formatted_events)

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; overflow: hidden; background-color: #03050c; font-family: 'Space Grotesk', sans-serif; }
            #hud-timeline {
                position: absolute; top: 12px; left: 12px;
                color: #cbd5e1; font-size: 11px; font-weight: 600;
                letter-spacing: 1.5px; text-transform: uppercase;
                pointer-events: none; z-index: 5;
            }
        </style>
    </head>
    <body>
        <div id="hud-timeline">__TITLE__</div>
        <div id="canvas-container" style="width: 100vw; height: 100vh;"></div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const events = __EVENTS__;

            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x03050c, 0.015);

            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 0, 75);

            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.enableZoom = false;

            // Ambient & directional lights
            const ambient = new THREE.AmbientLight(0xffffff, 0.3);
            scene.add(ambient);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.85);
            dirLight.position.set(10, 20, 30);
            scene.add(dirLight);

            // Double Helix Track spline construction
            const curvePoints = [];
            const curvePointsB = [];
            const numPoints = 80;
            const helixRadius = 15;
            const heightSpan = 50;

            for (let i = 0; i < numPoints; i++) {
                const t = i / (numPoints - 1);
                const angle = t * Math.PI * 6; // 3 full turns
                const y = -heightSpan/2 + t * heightSpan;

                // Helix Strand A
                const xA = Math.cos(angle) * helixRadius;
                const zA = Math.sin(angle) * helixRadius;
                curvePoints.push(new THREE.Vector3(xA, y, zA));

                // Helix Strand B (180 degree phase shift)
                const xB = Math.cos(angle + Math.PI) * helixRadius;
                const zB = Math.sin(angle + Math.PI) * helixRadius;
                curvePointsB.push(new THREE.Vector3(xB, y, zB));
            }

            const splineA = new THREE.CatmullRomCurve3(curvePoints);
            const splineB = new THREE.CatmullRomCurve3(curvePointsB);

            // Render Spline Tubes (Strands)
            const tubeGeomA = new THREE.TubeGeometry(splineA, 100, 0.25, 8, false);
            const tubeGeomB = new THREE.TubeGeometry(splineB, 100, 0.25, 8, false);
            
            const strandMatA = new THREE.MeshBasicMaterial({ color: 0x00f0ff, transparent: true, opacity: 0.15 });
            const strandMatB = new THREE.MeshBasicMaterial({ color: 0xff007f, transparent: true, opacity: 0.15 });

            scene.add(new THREE.Mesh(tubeGeomA, strandMatA));
            scene.add(new THREE.Mesh(tubeGeomB, strandMatB));

            // Plot messages along strands
            const messageNodes = [];
            
            if (events && events.length > 0) {
                events.forEach((evt, idx) => {
                    // Position along index fraction
                    const t = (idx + 0.5) / (events.length + 0.5);
                    const ptA = splineA.getPointAt(t);
                    const ptB = splineB.getPointAt(t);

                    // Choose geometry based on toxicity
                    // Safe = Sleek Octahedron. Toxic = Spike Sphere.
                    let geom;
                    if (evt.is_toxic) {
                        geom = new THREE.DodecahedronGeometry(2.2);
                    } else {
                        geom = new THREE.OctahedronGeometry(2.0);
                    }

                    // Premium holographic frosted material
                    const nodeMat = new THREE.MeshPhysicalMaterial({
                        color: new THREE.Color(evt.color),
                        transparent: true,
                        opacity: 0.8,
                        roughness: 0.1,
                        transmission: 0.6,
                        thickness: 1.0,
                        ior: 1.45,
                        emissive: new THREE.Color(evt.color),
                        emissiveIntensity: 0.25
                    });

                    const nodeMesh = new THREE.Mesh(geom, nodeMat);
                    nodeMesh.position.copy(ptA);
                    scene.add(nodeMesh);
                    messageNodes.push(nodeMesh);

                    // Add dynamic neon outline wireframe
                    const edges = new THREE.EdgesGeometry(geom);
                    const lineMat = new THREE.LineBasicMaterial({
                        color: new THREE.Color(evt.color),
                        transparent: true,
                        opacity: 0.9,
                        blending: THREE.AdditiveBlending
                    });
                    const wireframe = new THREE.LineSegments(edges, lineMat);
                    nodeMesh.add(wireframe);

                    // Connect strands A and B at node height with a grid rung
                    const rungPoints = [ptA, ptB];
                    const rungGeom = new THREE.BufferGeometry().setFromPoints(rungPoints);
                    const rungMat = new THREE.LineBasicMaterial({
                        color: 0x1f2937,
                        transparent: true,
                        opacity: 0.35
                    });
                    const rung = new THREE.Line(rungGeom, rungMat);
                    scene.add(rung);
                });
            }

            // Animation Loop
            let angle = 0;
            function animate() {
                requestAnimationFrame(animate);
                angle += 0.003;

                // Slow rotation
                scene.rotation.y = angle;

                // Animate nodes pulsing and spinning
                messageNodes.forEach((node, i) => {
                    node.rotation.x += 0.008 * (i + 1);
                    node.rotation.y += 0.004 * (i + 1);
                    
                    const scaleFactor = 1.0 + Math.sin(angle * 10 + i) * 0.08;
                    node.scale.set(scaleFactor, scaleFactor, scaleFactor);
                });

                controls.update();
                renderer.render(scene, camera);
            }
            animate();

            // Resize support
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        </script>
    </body>
    </html>
    """.replace("__TITLE__", title).replace("__EVENTS__", events_json)
    return html_template


def get_3d_pie_chart(labels, values, title, height=350):
    """
    Renders the 3D Volumetric Segmented Donut Chart.
    Plots toxicity metrics or message safe ratio into interactive WebGL ring segments.
    """
    # Color mapping for categories
    colors_map = {
        "Threat": "#ff007f",      # Crimson
        "Insult": "#ffaa00",      # Orange
        "Harassment": "#ffd700",  # Gold
        "Hate Speech": "#9b59b6",  # Purple
        "Safe": "#00f0ff",        # Cyan
    }

    default_colors = ["#00f0ff", "#ffaa00", "#ffd700", "#9b59b6", "#ff007f"]
    chart_colors = [colors_map.get(lbl, default_colors[i % len(default_colors)]) for i, lbl in enumerate(labels)]

    data_json = json.dumps([{"label": lbl, "val": val, "color": chart_colors[i]} for i, (lbl, val) in enumerate(zip(labels, values))])

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { margin: 0; overflow: hidden; background-color: #03050c; font-family: 'Space Grotesk', sans-serif; }
            #hud-donut {
                position: absolute; top: 12px; left: 12px;
                color: #cbd5e1; font-size: 11px; font-weight: 600;
                letter-spacing: 1.5px; text-transform: uppercase;
                pointer-events: none; z-index: 5;
            }
        </style>
    </head>
    <body>
        <div id="hud-donut">__TITLE__</div>
        <div id="canvas-container" style="width: 100vw; height: 100vh;"></div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const data = __DATA__;

            const scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x03050c, 0.02);

            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 25, 45);

            const renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2.1;
            controls.enableZoom = false;

            // Lights
            const ambient = new THREE.AmbientLight(0xffffff, 0.45);
            scene.add(ambient);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.85);
            dirLight.position.set(10, 30, 10);
            scene.add(dirLight);

            // Compute total value
            const total = data.reduce((sum, item) => sum + item.val, 0);

            // Render Donut Slices
            let startAngle = 0;
            const segments = [];

            if (total > 0) {
                data.forEach((item, index) => {
                    const sweep = (item.val / total) * 6.283185307179586; // 2 * Math.PI
                    
                    // Create ring sector geometry
                    const geom = new THREE.RingGeometry(10, 14, 32, 1, startAngle, sweep);
                    
                    // Extrude to create volumetric depth
                    const extrudeSettings = {
                        depth: 4,
                        steps: 1,
                        bevelEnabled: true,
                        bevelThickness: 0.3,
                        bevelSize: 0.15,
                        bevelSegments: 2
                    };

                    // Material physical attributes (glass look)
                    const material = new THREE.MeshPhysicalMaterial({
                        color: new THREE.Color(item.color),
                        transparent: true,
                        opacity: 0.7,
                        roughness: 0.12,
                        transmission: 0.4,
                        thickness: 1.0,
                        ior: 1.45,
                        side: THREE.DoubleSide
                    });

                    // Shape extrusion helpers
                    const shape = new THREE.Shape();
                    
                    // Approximating ring sector in shapes
                    const thetaStart = startAngle;
                    const thetaEnd = startAngle + sweep;
                    
                    // Add shape geometry segment
                    const outerR = 12;
                    const innerR = 8.5;
                    
                    shape.moveTo(Math.cos(thetaStart) * innerR, Math.sin(thetaStart) * innerR);
                    shape.lineTo(Math.cos(thetaStart) * outerR, Math.sin(thetaStart) * outerR);
                    shape.absarc(0, 0, outerR, thetaStart, thetaEnd, false);
                    shape.lineTo(Math.cos(thetaEnd) * innerR, Math.sin(thetaEnd) * innerR);
                    shape.absarc(0, 0, innerR, thetaEnd, thetaStart, true);

                    const extrudeGeom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
                    // Center the extrusion coordinate y offset
                    extrudeGeom.center();

                    const mesh = new THREE.Mesh(extrudeGeom, material);
                    
                    // Rotation alignment flat
                    mesh.rotation.x = Math.PI / 2;
                    mesh.position.y = 0;
                    scene.add(mesh);
                    segments.push(mesh);

                    // Wireframe outline
                    const edges = new THREE.EdgesGeometry(extrudeGeom);
                    const lineMat = new THREE.LineBasicMaterial({
                        color: new THREE.Color(item.color),
                        transparent: true,
                        opacity: 0.85,
                        blending: THREE.AdditiveBlending
                    });
                    const wireframe = new THREE.LineSegments(edges, lineMat);
                    mesh.add(wireframe);

                    startAngle += sweep;
                });
            } else {
                // Render default empty ring
                const shape = new THREE.Shape();
                shape.absarc(0, 0, 11, 0, Math.PI * 2, false);
                
                const hole = new THREE.Path();
                hole.absarc(0, 0, 8, 0, Math.PI * 2, true);
                shape.holes.push(hole);

                const extrudeGeom = new THREE.ExtrudeGeometry(shape, { depth: 3, bevelEnabled: true });
                extrudeGeom.center();
                
                const mesh = new THREE.Mesh(extrudeGeom, new THREE.MeshPhysicalMaterial({
                    color: 0x1f2937,
                    transparent: true,
                    opacity: 0.35
                }));
                mesh.rotation.x = Math.PI / 2;
                scene.add(mesh);
            }

            // Grid support
            const gridHelper = new THREE.GridHelper(50, 10, 0x1f2937, 0x111827);
            gridHelper.position.y = -3;
            scene.add(gridHelper);

            // Animation Loop
            let angle = 0;
            function animate() {
                requestAnimationFrame(animate);
                angle += 0.003;

                // Slow mesh rotation
                scene.rotation.y = angle * 0.8;

                // Small concentric segment expansion effect
                segments.forEach((seg, i) => {
                    const scaleFactor = 1.0 + Math.sin(angle * 12 + i) * 0.03;
                    seg.scale.set(scaleFactor, scaleFactor, 1);
                });

                controls.update();
                renderer.render(scene, camera);
            }
            animate();

            // Resize support
            window.addEventListener('resize', () => {
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            });
        </script>
    </body>
    </html>
    """.replace("__TITLE__", title).replace("__DATA__", data_json)
    return html_template
