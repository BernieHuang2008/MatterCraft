"""WebGL viewer generator for modern MatterCraft visualizer windows."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
import json
from pathlib import Path
import tempfile
from typing import Any
import webbrowser

from debug_module import log

from .common import VisualModel, VisualizerRequest


WEBGL_VIEWER_RUNTIME_DIR = Path(tempfile.gettempdir()) / "mattercraft_visualizer"


def openWebglVisualizerWindow(
    title: str,
    sourceObject: object,
    visualizer: object,
    request: VisualizerRequest,
) -> Path:
    """
    Function:
        Generate and open one local WebGL visualizer page.
    Args:
        title: Browser window title.
        sourceObject: Matter-core object to visualize.
        visualizer: Visualizer instance.
        request: Initial visualizer request.
    Returns:
        Path: Generated HTML file path.
    Implementation Logic:
        The Python app builds the renderer-neutral VisualModel once, embeds it
        into a self-contained WebGL HTML file and opens that local file in the
        user's browser.
    """

    build_method = getattr(visualizer, "buildVisualModel")
    model = build_method(sourceObject, request)
    html_path = writeWebglVisualizerHtml(title=title, model=model)
    webbrowser.open(html_path.as_uri())
    log(
        level="info",
        module="visualizer.webgl_viewer",
        message="WebGL visualizer opened.",
        context={"title": title, "path": str(html_path)},
    )
    return html_path


def writeWebglVisualizerHtml(title: str, model: VisualModel) -> Path:
    """
    Function:
        Write one self-contained WebGL viewer HTML file.
    Args:
        title: HTML document title.
        model: Visual model to embed.
    Returns:
        Path: Generated HTML path.
    Implementation Logic:
        The generated file is static and dependency-free, relying only on native
        browser WebGL plus CSS HUD overlays.
    """

    WEBGL_VIEWER_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = model._id.replace(".", "_").replace(":", "_")
    html_path = WEBGL_VIEWER_RUNTIME_DIR / f"{safe_name}.html"
    model_json = json.dumps(_toSerializable(model), ensure_ascii=False)
    html_path.write_text(_buildHtml(title=title, modelJson=model_json), encoding="utf-8")
    return html_path


def _toSerializable(value: Any) -> Any:
    """
    Function:
        Convert dataclass-heavy visual model data into JSON-serializable values.
    Args:
        value: Arbitrary value.
    Returns:
        Any: JSON-serializable value.
    Implementation Logic:
        Visual models are nested dataclasses, so conversion recursively handles
        dataclasses, lists, tuples and dictionaries before JSON encoding.
    """

    if is_dataclass(value):
        return _toSerializable(asdict(value))
    if isinstance(value, dict):
        return {str(key): _toSerializable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_toSerializable(item) for item in value]
    return value


def _buildHtml(title: str, modelJson: str) -> str:
    """
    Function:
        Build the self-contained WebGL viewer HTML.
    Args:
        title: HTML document title.
        modelJson: Serialized visual model JSON.
    Returns:
        str: HTML content.
    Implementation Logic:
        CSS creates fixed screen-space HUD panels while JavaScript renders the
        model in WebGL and keeps labels/HUD independent of camera rotation.
    """

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{_escapeHtml(title)}</title>
  <style>
    :root {{
      color-scheme: dark;
      --glass: rgba(4, 8, 14, 0.72);
      --glass-strong: rgba(4, 8, 14, 0.86);
      --line: rgba(168, 198, 255, 0.22);
      --text: #edf5ff;
      --muted: #91a1b8;
      --accent: #76d7ff;
      --hot: #ffb464;
    }}
    html, body {{
      margin: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
      background: #02050a;
      font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
      letter-spacing: 0;
    }}
    #gl {{
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      display: block;
      background:
        radial-gradient(circle at 50% 48%, rgba(38, 68, 112, 0.24), transparent 42%),
        linear-gradient(180deg, #03060b 0%, #090d14 100%);
    }}
    .hud {{
      position: fixed;
      z-index: 3;
      color: var(--text);
      user-select: none;
      pointer-events: none;
    }}
    .topbar {{
      top: 18px;
      left: 18px;
      right: 18px;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
    }}
    .titleBlock {{
      max-width: min(580px, calc(100vw - 420px));
      padding: 14px 16px 13px;
      background: var(--glass);
      border: 1px solid var(--line);
      backdrop-filter: blur(18px) saturate(1.2);
      box-shadow: 0 16px 50px rgba(0,0,0,0.38);
    }}
    .titleBlock h1 {{
      margin: 0 0 6px;
      font-size: 16px;
      font-weight: 650;
      color: var(--text);
    }}
    .titleBlock .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-family: "Cascadia Mono", Consolas, monospace;
      font-size: 11px;
    }}
    .chip {{
      padding: 4px 7px;
      border: 1px solid rgba(255,255,255,0.10);
      background: rgba(255,255,255,0.045);
    }}
    .panel {{
      top: 92px;
      right: 18px;
      bottom: 96px;
      width: min(390px, calc(100vw - 36px));
      overflow: auto;
      padding: 14px;
      background: var(--glass-strong);
      border: 1px solid var(--line);
      backdrop-filter: blur(22px) saturate(1.25);
      box-shadow: 0 24px 70px rgba(0,0,0,0.48);
    }}
    .section {{
      padding: 12px 0;
      border-top: 1px solid rgba(255,255,255,0.08);
    }}
    .section:first-child {{
      border-top: 0;
      padding-top: 0;
    }}
    .sectionTitle {{
      margin: 0 0 10px;
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
    }}
    .row {{
      display: grid;
      grid-template-columns: minmax(96px, 36%) 1fr;
      gap: 12px;
      margin: 7px 0;
      font-size: 12px;
      line-height: 1.35;
    }}
    .key {{
      color: var(--muted);
    }}
    .value {{
      color: var(--text);
      overflow-wrap: anywhere;
    }}
    .code {{
      font-family: "Cascadia Mono", Consolas, monospace;
      color: #dce8ff;
    }}
    .notation {{
      left: 18px;
      right: 18px;
      bottom: 18px;
      min-height: 54px;
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 16px;
      background: rgba(1, 4, 9, 0.78);
      border: 1px solid var(--line);
      backdrop-filter: blur(20px) saturate(1.25);
      box-shadow: 0 -16px 50px rgba(0,0,0,0.42);
    }}
    .notationLabel {{
      color: var(--muted);
      font-size: 11px;
      text-transform: uppercase;
      white-space: nowrap;
    }}
    .notationText {{
      font-family: "Cascadia Mono", Consolas, monospace;
      font-size: 18px;
      font-weight: 650;
      color: #f4f9ff;
      overflow-wrap: anywhere;
    }}
    .nodeLabel {{
      position: fixed;
      z-index: 2;
      transform: translate(-50%, -50%);
      padding: 3px 6px;
      color: #eff7ff;
      background: rgba(0, 0, 0, 0.42);
      border: 1px solid rgba(255,255,255,0.14);
      font-family: "Cascadia Mono", Consolas, monospace;
      font-size: 11px;
      pointer-events: none;
      backdrop-filter: blur(12px);
    }}
    .nodeLabel.selected {{
      color: #05070b;
      background: var(--hot);
      border-color: rgba(255,255,255,0.55);
    }}
    @media (max-width: 780px) {{
      .topbar {{
        left: 10px;
        right: 10px;
        top: 10px;
      }}
      .titleBlock {{
        max-width: calc(100vw - 20px);
      }}
      .panel {{
        left: 10px;
        right: 10px;
        top: auto;
        bottom: 86px;
        width: auto;
        max-height: 38vh;
      }}
      .notation {{
        left: 10px;
        right: 10px;
        bottom: 10px;
      }}
      .notationText {{
        font-size: 15px;
      }}
    }}
  </style>
</head>
<body>
  <canvas id="gl"></canvas>
  <div id="labels"></div>
  <div class="hud topbar">
    <div class="titleBlock">
      <h1 id="title"></h1>
      <div class="meta">
        <span class="chip" id="sourceType"></span>
        <span class="chip" id="mode"></span>
        <span class="chip" id="state"></span>
      </div>
    </div>
  </div>
  <aside class="hud panel" id="panel"></aside>
  <div class="hud notation">
    <div class="notationLabel">Electron Notation</div>
    <div class="notationText" id="notation"></div>
  </div>
  <script>
    const model = {modelJson};
    const canvas = document.getElementById('gl');
    const labelLayer = document.getElementById('labels');
    const gl = canvas.getContext('webgl', {{ antialias: true, alpha: false }});
    if (!gl) {{
      document.body.innerHTML = '<div style="padding:24px;color:white;background:#05070b;font-family:sans-serif">WebGL is not available in this browser.</div>';
      throw new Error('WebGL unavailable');
    }}

    const camera = {{
      rx: model.bScene.bCameraState.bRotationX || 0,
      ry: model.bScene.bCameraState.bRotationY || 0,
      panX: model.bScene.bCameraState.bPanX || 0,
      panY: model.bScene.bCameraState.bPanY || 0,
      zoom: model.bScene.bCameraState.bZoom || 90,
      minZoom: model.bScene.bCameraState.bMinZoom || 24,
      maxZoom: model.bScene.bCameraState.bMaxZoom || 420
    }};
    const pointer = {{ button: null, sx: 0, sy: 0, lx: 0, ly: 0, dragged: false }};
    let selectedNodeId = model.bSelectionState.bSelectedObjectId || null;
    let dpr = 1;

    const vertexSource = `
      attribute vec3 aPosition;
      attribute vec3 aColor;
      attribute float aSize;
      uniform vec2 uResolution;
      uniform float uDpr;
      varying vec3 vColor;
      void main() {{
        vec2 zeroToOne = aPosition.xy / uResolution;
        vec2 clip = zeroToOne * 2.0 - 1.0;
        gl_Position = vec4(clip.x, -clip.y, 0.0, 1.0);
        gl_PointSize = aSize * uDpr;
        vColor = aColor;
      }}
    `;
    const fragmentSource = `
      precision mediump float;
      varying vec3 vColor;
      void main() {{
        vec2 p = gl_PointCoord - vec2(0.5);
        float d = length(p);
        if (d > 0.5) discard;
        float shade = smoothstep(0.5, 0.05, d);
        vec3 color = vColor * (0.56 + 0.44 * shade);
        gl_FragColor = vec4(color, 1.0);
      }}
    `;
    const lineVertexSource = `
      attribute vec3 aPosition;
      attribute vec3 aColor;
      uniform vec2 uResolution;
      varying vec3 vColor;
      void main() {{
        vec2 zeroToOne = aPosition.xy / uResolution;
        vec2 clip = zeroToOne * 2.0 - 1.0;
        gl_Position = vec4(clip.x, -clip.y, 0.0, 1.0);
        vColor = aColor;
      }}
    `;
    const lineFragmentSource = `
      precision mediump float;
      varying vec3 vColor;
      void main() {{
        gl_FragColor = vec4(vColor, 1.0);
      }}
    `;

    const pointProgram = createProgram(vertexSource, fragmentSource);
    const lineProgram = createProgram(lineVertexSource, lineFragmentSource);
    const pointBuffers = createBuffers(pointProgram);
    const lineBuffers = createBuffers(lineProgram);

    function createProgram(vs, fs) {{
      const program = gl.createProgram();
      gl.attachShader(program, compile(gl.VERTEX_SHADER, vs));
      gl.attachShader(program, compile(gl.FRAGMENT_SHADER, fs));
      gl.linkProgram(program);
      if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
      return program;
    }}
    function compile(type, source) {{
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
      return shader;
    }}
    function createBuffers(program) {{
      return {{
        position: gl.createBuffer(),
        color: gl.createBuffer(),
        size: gl.createBuffer(),
        positionLoc: gl.getAttribLocation(program, 'aPosition'),
        colorLoc: gl.getAttribLocation(program, 'aColor'),
        sizeLoc: gl.getAttribLocation(program, 'aSize'),
        resolutionLoc: gl.getUniformLocation(program, 'uResolution'),
        dprLoc: gl.getUniformLocation(program, 'uDpr')
      }};
    }}

    function resize() {{
      dpr = Math.max(1, Math.min(2.5, window.devicePixelRatio || 1));
      const width = Math.floor(window.innerWidth * dpr);
      const height = Math.floor(window.innerHeight * dpr);
      if (canvas.width !== width || canvas.height !== height) {{
        canvas.width = width;
        canvas.height = height;
        canvas.style.width = window.innerWidth + 'px';
        canvas.style.height = window.innerHeight + 'px';
      }}
      gl.viewport(0, 0, canvas.width, canvas.height);
    }}

    function project(position) {{
      const x = position[0], y = position[1], z = position[2];
      const cy = Math.cos(camera.ry), sy = Math.sin(camera.ry);
      const rx = x * cy + z * sy;
      const rz = -x * sy + z * cy;
      const cx = Math.cos(camera.rx), sx = Math.sin(camera.rx);
      const ry = y * cx - rz * sx;
      const depth = y * sx + rz * cx;
      return {{
        x: window.innerWidth / 2 + camera.panX + rx * camera.zoom,
        y: window.innerHeight / 2 + camera.panY - ry * camera.zoom,
        depth
      }};
    }}
    function colorForNode(node) {{
      if (node.bStyle && node.bStyle.color) return hexToRgb(node.bStyle.color);
      const palette = {{
        nucleus: '#ff9e59',
        atom: '#5fb7ff',
        bond: '#d7b96b',
        subshell: '#6d87ff',
        atomic_core: '#8ac6ff',
        orbital_box: '#31465f',
        electron_arrow: '#f7d36b',
        orbital_cloud: '#6aa8ff',
        molecule: '#4fbf9f',
        interaction: '#d98b6a',
        component: '#a6c75f'
      }};
      return hexToRgb(palette[node.bNodeType] || '#6f7d90');
    }}
    function hexToRgb(hex) {{
      const clean = hex.replace('#', '');
      const number = parseInt(clean.length === 3 ? clean.split('').map(x => x + x).join('') : clean, 16);
      return [((number >> 16) & 255) / 255, ((number >> 8) & 255) / 255, (number & 255) / 255];
    }}

    function draw() {{
      resize();
      gl.clearColor(0.01, 0.018, 0.032, 1);
      gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
      drawEdges();
      drawNodes();
      drawLabels();
      renderHud();
      requestAnimationFrame(draw);
    }}
    function drawEdges() {{
      const nodeMap = new Map(model.bScene.bNodeList.map(node => [node._id, node]));
      const positions = [];
      const colors = [];
      for (const edge of model.bScene.bEdgeList) {{
        const source = nodeMap.get(edge.bSourceNodeId);
        const target = nodeMap.get(edge.bTargetNodeId);
        if (!source || !target) continue;
        const a = project(source.bPosition);
        const b = project(target.bPosition);
        const c = edge.bIsSelected ? hexToRgb('#ffb464') : hexToRgb('#667995');
        positions.push(a.x, a.y, 0, b.x, b.y, 0);
        colors.push(...c, ...c);
      }}
      if (!positions.length) return;
      gl.useProgram(lineProgram);
      bindArray(lineBuffers.position, lineBuffers.positionLoc, positions, 3);
      bindArray(lineBuffers.color, lineBuffers.colorLoc, colors, 3);
      gl.uniform2f(lineBuffers.resolutionLoc, window.innerWidth, window.innerHeight);
      gl.lineWidth(2);
      gl.drawArrays(gl.LINES, 0, positions.length / 3);
    }}
    function drawNodes() {{
      const positions = [];
      const colors = [];
      const sizes = [];
      for (const node of model.bScene.bNodeList) {{
        if (!node.bIsVisible) continue;
        const p = project(node.bPosition);
        const c = selectedNodeId === node._id || node.bIsSelected ? hexToRgb('#ffb464') : colorForNode(node);
        positions.push(p.x, p.y, p.depth);
        colors.push(...c);
        sizes.push(Math.max(12, node.bHitRadius * 1.55));
      }}
      if (!positions.length) return;
      gl.useProgram(pointProgram);
      bindArray(pointBuffers.position, pointBuffers.positionLoc, positions, 3);
      bindArray(pointBuffers.color, pointBuffers.colorLoc, colors, 3);
      bindArray(pointBuffers.size, pointBuffers.sizeLoc, sizes, 1);
      gl.uniform2f(pointBuffers.resolutionLoc, window.innerWidth, window.innerHeight);
      gl.uniform1f(pointBuffers.dprLoc, dpr);
      gl.drawArrays(gl.POINTS, 0, positions.length / 3);
    }}
    function bindArray(buffer, loc, data, size) {{
      gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
      gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data), gl.DYNAMIC_DRAW);
      gl.enableVertexAttribArray(loc);
      gl.vertexAttribPointer(loc, size, gl.FLOAT, false, 0, 0);
    }}
    function drawLabels() {{
      labelLayer.innerHTML = '';
      for (const node of model.bScene.bNodeList) {{
        if (!node.bIsVisible) continue;
        const p = project(node.bPosition);
        if (p.x < -80 || p.x > window.innerWidth + 80 || p.y < -80 || p.y > window.innerHeight + 80) continue;
        const label = document.createElement('div');
        label.className = 'nodeLabel' + ((selectedNodeId === node._id || node.bIsSelected) ? ' selected' : '');
        label.textContent = node.bLabel;
        label.style.left = p.x + 'px';
        label.style.top = (p.y - node.bHitRadius - 14) + 'px';
        labelLayer.appendChild(label);
      }}
    }}
    function hitTest(x, y) {{
      let best = null;
      let bestDistance = Infinity;
      for (const node of model.bScene.bNodeList) {{
        if (!node.bIsInteractive || !node.bIsVisible) continue;
        const p = project(node.bPosition);
        const distance = Math.hypot(x - p.x, y - p.y);
        if (distance <= node.bHitRadius && distance < bestDistance) {{
          best = node;
          bestDistance = distance;
        }}
      }}
      return best;
    }}
    canvas.addEventListener('pointerdown', event => {{
      pointer.button = event.button === 1 ? 'middle' : 'left';
      pointer.sx = pointer.lx = event.clientX;
      pointer.sy = pointer.ly = event.clientY;
      pointer.dragged = false;
      canvas.setPointerCapture(event.pointerId);
    }});
    canvas.addEventListener('pointermove', event => {{
      if (!pointer.button) return;
      const dx = event.clientX - pointer.lx;
      const dy = event.clientY - pointer.ly;
      if (Math.hypot(event.clientX - pointer.sx, event.clientY - pointer.sy) > 4) pointer.dragged = true;
      if (pointer.button === 'middle') {{
        camera.panX += dx;
        camera.panY += dy;
      }} else if (pointer.button === 'left' && pointer.dragged) {{
        camera.ry += dx * 0.01;
        camera.rx += dy * 0.01;
      }}
      pointer.lx = event.clientX;
      pointer.ly = event.clientY;
    }});
    canvas.addEventListener('pointerup', event => {{
      if (pointer.button === 'left' && !pointer.dragged) {{
        const hit = hitTest(event.clientX, event.clientY);
        selectedNodeId = hit ? hit._id : null;
      }}
      pointer.button = null;
    }});
    canvas.addEventListener('wheel', event => {{
      event.preventDefault();
      const oldZoom = camera.zoom;
      const viewX = (event.clientX - window.innerWidth / 2 - camera.panX) / oldZoom;
      const viewY = -((event.clientY - window.innerHeight / 2 - camera.panY) / oldZoom);
      const factor = event.deltaY < 0 ? 1.12 : 1 / 1.12;
      camera.zoom = Math.max(camera.minZoom, Math.min(camera.maxZoom, camera.zoom * factor));
      camera.panX = event.clientX - window.innerWidth / 2 - viewX * camera.zoom;
      camera.panY = event.clientY - window.innerHeight / 2 + viewY * camera.zoom;
    }}, {{ passive: false }});

    function renderHud() {{
      document.getElementById('title').textContent = model.bPanel.bTitle;
      document.getElementById('sourceType').textContent = model.bSourceObjectType;
      document.getElementById('mode').textContent = model.bMode;
      document.getElementById('state').textContent = selectedNodeId || model.bSelectionState.bStateName;
      document.getElementById('notation').textContent = resolveNotation();
      renderPanel();
    }}
    function resolveNotation() {{
      for (const section of model.bPanel.bSectionList) {{
        for (const entry of section.bEntryList || []) {{
          if (entry.bLabel === 'Visible Notation' || entry.bLabel === 'Box View') return entry.bValue;
        }}
      }}
      return model.bSourceObjectType + '  ' + model.bSourceObjectId;
    }}
    function renderPanel() {{
      const panel = document.getElementById('panel');
      if (panel.dataset.renderedFor === selectedNodeId) return;
      panel.dataset.renderedFor = selectedNodeId || '';
      panel.innerHTML = '';
      for (const section of model.bPanel.bSectionList) {{
        const sectionEl = document.createElement('section');
        sectionEl.className = 'section';
        const title = document.createElement('h2');
        title.className = 'sectionTitle';
        title.textContent = section.bTitle;
        sectionEl.appendChild(title);
        for (const entry of section.bEntryList || []) {{
          const row = document.createElement('div');
          row.className = 'row';
          const key = document.createElement('div');
          key.className = 'key';
          key.textContent = entry.bLabel;
          const value = document.createElement('div');
          value.className = 'value' + (entry.bValueType === 'code' ? ' code' : '');
          value.textContent = entry.bValue;
          row.appendChild(key);
          row.appendChild(value);
          sectionEl.appendChild(row);
        }}
        for (const line of section.bNarrativeLineList || []) {{
          const row = document.createElement('div');
          row.className = 'row';
          row.innerHTML = '<div class="key"></div><div class="value">' + escapeHtml(line) + '</div>';
          sectionEl.appendChild(row);
        }}
        panel.appendChild(sectionEl);
      }}
      if (selectedNodeId) {{
        const hit = model.bScene.bNodeList.find(node => node._id === selectedNodeId);
        if (hit) {{
          const selected = document.createElement('section');
          selected.className = 'section';
          selected.innerHTML = '<h2 class="sectionTitle">Selected Node</h2>';
          for (const [key, value] of Object.entries(hit.bPayload || {{}})) {{
            const row = document.createElement('div');
            row.className = 'row';
            row.innerHTML = '<div class="key">' + escapeHtml(key) + '</div><div class="value code">' + escapeHtml(String(value)) + '</div>';
            selected.appendChild(row);
          }}
          panel.appendChild(selected);
        }}
      }}
    }}
    function escapeHtml(text) {{
      return text.replace(/[&<>"']/g, ch => ({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[ch]));
    }}
    window.addEventListener('resize', resize);
    draw();
  </script>
</body>
</html>"""


def _escapeHtml(value: str) -> str:
    """
    Function:
        Escape a small string for HTML text context.
    Args:
        value: Raw string.
    Returns:
        str: Escaped string.
    Implementation Logic:
        The title is inserted into the generated document before JavaScript
        takes over rendering, so it needs normal HTML escaping.
    """

    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
