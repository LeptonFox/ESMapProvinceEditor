<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Binary Province Map Generator</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; }
        input[type="file"] { margin: 20px; }
        #output-section { display: flex; justify-content: center; flex-wrap: wrap; margin-top: 20px; }
        .canvas-container { margin: 10px; }
        canvas { border: 1px solid #333; max-width: 100%; }
        #console-panel {
            margin-top: 20px;
            padding: 10px;
            background-color: #f1f1f1;
            border: 1px solid #ccc;
            max-width: 600px;
            margin: 20px auto;
            text-align: left;
            font-size: 0.9em;
            color: #333;
            height: 150px;
            overflow-y: auto;
            white-space: pre-line;
        }
    </style>
</head>
<body>
    <h1>Binary Province Map Generator</h1>
    <p>Upload a map image to convert it to a binary water-land map.</p>
    <input type="file" id="mapInput" accept="image/*">
    <button onclick="processMap()">Generate Binary Map</button>

    <!-- Console Panel -->
    <div id="console-panel"></div>

    <div class="canvas-container">
        <h3>Configuration Variables</h3>
        <table style="margin: 0 auto;">
            <tr>
                <td>Red Threshold:</td>
                <td><input type="number" id="redThreshold" value="100" min="0" max="255"></td>
                <td><input type="checkbox" id="useRedThreshold"> Enable</td>
            </tr>
            <tr>
                <td>Green Threshold:</td>
                <td><input type="number" id="greenThreshold" value="100" min="0" max="255"></td>
                <td><input type="checkbox" id="useGreenThreshold"> Enable</td>
            </tr>
            <tr>
                <td>Blue Threshold:</td>
                <td><input type="number" id="blueThreshold" value="130" min="0" max="255"></td>
                <td><input type="checkbox" id="useBlueThreshold"> Enable</td>
            </tr>
            <tr>
                <td>Brightness Threshold:</td>
                <td><input type="number" id="brightnessThreshold" value="100" min="0" max="255"></td>
                <td><input type="checkbox" id="useBrightnessThreshold"> Enable</td>
            </tr>
        </table>
    </div>

    <div id="output-section">
        <div class="canvas-container">
            <h3>Original Map</h3>
            <canvas id="original-canvas"></canvas>
        </div>
        <div class="canvas-container">
            <h3>Binary Map</h3>
            <canvas id="binary-canvas"></canvas>
        </div>
        <div class="canvas-container">
            <h3>Overlay Map</h3>
            <canvas id="overlay-canvas"></canvas>
        </div>
    </div>

    <script>
        function logToConsole(message) {
            const consolePanel = document.getElementById('console-panel');
            consolePanel.innerText += message + '\n';
            consolePanel.scrollTop = consolePanel.scrollHeight;
        }

        function processMap() {
            const fileInput = document.getElementById('mapInput');
            if (!fileInput.files.length) {
                alert("Please select a file.");
                logToConsole("Error: No file selected.");
                return;
            }

            const file = fileInput.files[0];
            const img = new Image();
            img.src = URL.createObjectURL(file);

            img.onload = () => {
                const originalCanvas = document.getElementById('original-canvas');
                const binaryCanvas = document.getElementById('binary-canvas');
                const overlayCanvas = document.getElementById('overlay-canvas');
                const originalContext = originalCanvas.getContext('2d');
                const binaryContext = binaryCanvas.getContext('2d');
                const overlayContext = overlayCanvas.getContext('2d');

                originalCanvas.width = binaryCanvas.width = overlayCanvas.width = img.width;
                originalCanvas.height = binaryCanvas.height = overlayCanvas.height = img.height;

                // Draw original image
                originalContext.drawImage(img, 0, 0);

                // Create binary map and overlay
                createBinaryAndOverlayMap(originalContext, binaryContext, overlayContext, img.width, img.height);
            };
        }

        function createBinaryAndOverlayMap(originalContext, binaryContext, overlayContext, width, height) {
            const imageData = originalContext.getImageData(0, 0, width, height);
            const data = imageData.data;
            const binaryData = new Uint8ClampedArray(data);

            const redThreshold = parseInt(document.getElementById("redThreshold").value, 10);
            const greenThreshold = parseInt(document.getElementById("greenThreshold").value, 10);
            const blueThreshold = parseInt(document.getElementById("blueThreshold").value, 10);
            const brightnessThreshold = parseInt(document.getElementById("brightnessThreshold").value, 10);

            const useRedThreshold = document.getElementById("useRedThreshold").checked;
            const useGreenThreshold = document.getElementById("useGreenThreshold").checked;
            const useBlueThreshold = document.getElementById("useBlueThreshold").checked;
            const useBrightnessThreshold = document.getElementById("useBrightnessThreshold").checked;

            logToConsole(`Processing with thresholds: Red ${redThreshold}, Green ${greenThreshold}, Blue ${blueThreshold}, Brightness ${brightnessThreshold}`);
            
            // Process pixels to create binary map
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i];
                const g = data[i + 1];
                const b = data[i + 2];
                const brightness = (r + g + b) / 3;

                // Determine if pixel is land based on thresholds
                let isLand = true;
                if (useRedThreshold && r < redThreshold) isLand = false;
                if (useGreenThreshold && g < greenThreshold) isLand = false;
                if (useBlueThreshold && b > blueThreshold) isLand = false;
                if (useBrightnessThreshold && brightness < brightnessThreshold) isLand = false;

                if (isLand) {
                    // Land color (white)
                    binaryData[i] = 255; 
                    binaryData[i + 1] = 255; 
                    binaryData[i + 2] = 255;
                } else {
                    // Water color (black)
                    binaryData[i] = 0;
                    binaryData[i + 1] = 0;
                    binaryData[i + 2] = 0;
                }
            }

            // Display binary image
            const binaryImageData = new ImageData(binaryData, width, height);
            binaryContext.putImageData(binaryImageData, 0, 0);

            // Overlay binary on original with 50% opacity
            overlayContext.drawImage(originalContext.canvas, 0, 0);
            overlayContext.globalAlpha = 0.5;
            overlayContext.drawImage(binaryContext.canvas, 0, 0);
            logToConsole("Binary map and overlay map generated.");
        }
    </script>
</body>
</html>
