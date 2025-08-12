import React, { useEffect, useRef, useState } from 'react';
import { socket } from '../../socket';
import './Camera.css';

const Camera = () => {
    const imgRef = useRef(null);
    const dotsContainerRef = useRef(null);
    const composRef = useRef(null);
    
    const [points, setPoints] = useState([]);
    const [camera, setCamera] = useState(null);

    const reconnectAttempts = useRef(0);
    const maxReconnectAttempts = 10;
    const reconnectDelayMs = 2000;

    const hsvRefs = {
        'h-min': useRef(null),
        'h-max': useRef(null),
        's-min': useRef(null),
        's-max': useRef(null),
        'v-min': useRef(null),
        'v-max': useRef(null),
    };

    const hsvOutputRef = useRef(null);
    const pointsOutputRef = useRef(null);
    const messageInfoRef = useRef(null);

    const connectCamera = () => {

        ws.onopen = () => {
            console.log('WebSocket connected');
            reconnectAttempts.current = 0;
            imgRef.current.style.display = '';
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.message.image) {
                if (composRef.current) {
                    composRef.current.textContent = data.message.compos;
                }
                imgRef.current.src = `data:image/jpeg;base64,${data.message.image}`;
            } else if (data.message) {
                if (messageInfoRef.current) {
                    messageInfoRef.current.textContent = data.message;
                }
            }
        };

        ws.onclose = (e) => {
            console.error('WebSocket closed unexpectedly', e);
            imgRef.current.style.display = 'none';
            setCamera(null);
            if (reconnectAttempts.current < maxReconnectAttempts) {
                reconnectAttempts.current++;
                setTimeout(connectCamera, reconnectDelayMs);
            }
        };

        ws.onerror = (e) => {
            console.error('WebSocket error:', e);
            ws.close();
        };
    };

    const sendHSV = () => {
        if (camera && camera.readyState === WebSocket.OPEN) {
            const hsv = {};
            Object.entries(hsvRefs).forEach(([id, ref]) => {
                hsv[id.replace('-', '_')] = parseInt(ref.current.value);
            });
            hsv.isTwo = false;
            camera.send(JSON.stringify({ type: 'hsv', data: hsv }));
        }
    };

    const updateHSVOutput = () => {
        const hMin = parseInt(hsvRefs['h-min'].current.value);
        const sMin = parseInt(hsvRefs['s-min'].current.value);
        const vMin = parseInt(hsvRefs['v-min'].current.value);
        const hMax = parseInt(hsvRefs['h-max'].current.value);
        const sMax = parseInt(hsvRefs['s-max'].current.value);
        const vMax = parseInt(hsvRefs['v-max'].current.value);
        hsvOutputRef.current.textContent =
            `np.array([${hMin}, ${sMin}, ${vMin}])\nnp.array([${hMax}, ${sMax}, ${vMax}])`;
    };

    const resetPoints = () => {
        setPoints([]);
        dotsContainerRef.current.innerHTML = '';
        if (pointsOutputRef.current) {
            pointsOutputRef.current.textContent = '[]';
        }
    };

    const addDot = (x, y) => {
        const dot = document.createElement('div');
        dot.className = 'dot';
        dot.style.left = x + 'px';
        dot.style.top = y + 'px';
        dotsContainerRef.current.appendChild(dot);
    };

    const updateSliderValueText = () => {
        ['h', 's', 'v'].forEach((c) => {
            const minVal = hsvRefs[`${c}-min`]?.current?.value;
            const maxVal = hsvRefs[`${c}-max`]?.current?.value;

            const minSpan = document.getElementById(`${c}-min-val`);
            const maxSpan = document.getElementById(`${c}-max-val`);

            if (minSpan) minSpan.textContent = minVal;
            if (maxSpan) maxSpan.textContent = maxVal;
        });
    };

    const handleImageClick = (event) => {
        if (points.length >= 4) resetPoints();
        const rect = imgRef.current.getBoundingClientRect();
        const x = Math.round(event.clientX - rect.left);
        const y = Math.round(event.clientY - rect.top);
        const newPoints = [...points, [x, y]];
        setPoints(newPoints);
        if (pointsOutputRef.current) {
            pointsOutputRef.current.textContent = JSON.stringify(newPoints);
        }
        addDot(x, y);
    };

    const handleChange = (e) => {
        const selectedValue = e.target.value;
        camera?.send(JSON.stringify({ type: 'change_state', value: selectedValue }));
    };

    useEffect(() => {
        connectCamera();
        window.addEventListener('keydown', (e) => {
            if (e.key.toLowerCase() === 'r') resetPoints();
        });
    }, []);

    return (
        <div className="container py-4">
            <div className="row">
                <div className="col-md-8 position-relative">
                    <img
                        ref={imgRef}
                        src=""
                        alt="Webcam Feed"
                        className="img-fluid border rounded"
                        onClick={handleImageClick}
                    />
                    <div id="dots-container" ref={dotsContainerRef}
                         className="position-absolute top-0 start-0 w-100 h-100"></div>
                </div>

                <div className="col-md-4">
                    <div className="p-3 border rounded bg-light mb-3">
                        {['h', 's', 'v'].flatMap(c => ([
                            <div key={`${c}-min`} className="mb-2">
                                <label className="form-label">
                                    {c.toUpperCase()} Min: <span id={`${c}-min-val`}>{hsvRefs[`${c}-min`]?.current?.value ?? 0}</span>
                                </label>
                                <input
                                    ref={hsvRefs[`${c}-min`]}
                                    type="range"
                                    min="0"
                                    max={c === 'h' ? 180 : 255}
                                    defaultValue="0"
                                    className="form-range"
                                    onInput={() => {
                                        sendHSV();
                                        updateHSVOutput();
                                        updateSliderValueText();
                                    }}
                                />
                            </div>,
                            <div key={`${c}-max`} className="mb-2">
                                <label className="form-label">
                                    {c.toUpperCase()} Max: <span id={`${c}-max-val`}>{hsvRefs[`${c}-max`]?.current?.value ?? 255}</span>
                                </label>
                                <input
                                    ref={hsvRefs[`${c}-max`]}
                                    type="range"
                                    min="0"
                                    max={c === 'h' ? 180 : 255}
                                    defaultValue={c === 'h' ? 180 : 255}
                                    className="form-range"
                                    onInput={() => {
                                        sendHSV();
                                        updateHSVOutput();
                                        updateSliderValueText();
                                    }}
                                />
                            </div>,
                        ]))}

                    </div>
                </div>
            </div>

            <div className="my-3 d-flex flex-wrap gap-2">
                <button className="btn btn-success"
                        onClick={() => camera?.send(JSON.stringify({ type: 'zapl' }))}>Забрать воду</button>
                <button className="btn btn-danger"
                        onClick={() => camera?.send(JSON.stringify({ type: 'water' }))}>Поставить запладку</button>

                <button className="btn btn-info" onClick={() => {
                    navigator.clipboard.writeText(JSON.stringify(points)).then(() => alert('Скопировано!'));
                }}>Скопировать точки</button>
            </div>

            <div ref={messageInfoRef} className="alert alert-info mt-4"></div>

            <div className="mt-3">
                <strong>Выбранные точки:</strong>
                <div ref={pointsOutputRef}>[]</div>
            </div>

            <div className="mt-3 p-3 bg-light rounded border">
                <pre ref={hsvOutputRef} style={{ fontFamily: 'monospace' }}></pre>
            </div>

            <div className="mt-2">
                <span>Компас: <span ref={composRef}>0</span></span>
            </div>

        </div>
    );
};

export default Camera;
