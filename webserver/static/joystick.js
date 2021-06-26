class JoystickCommand {

    constructor() {
        this.left = new Map()
        this.left['LEFT'] = '97'
        this.left['RIGHT'] = '100'
        this.left['UP'] = '119'
        this.left['DOWN'] = '115'

        this.right = new Map()
        this.right['LEFT'] = '1073741904'
        this.right['RIGHT'] = '1073741903'
        this.right['UP'] = '1073741906'
        this.right['DOWN'] = '1073741905'
    }

    sendCommand = async (command, value) => {
        const response = await fetch('http://localhost:8080/api/control?command=' + command + '&value=' + value);
        const myJson = await response.json();
        console.log(myJson)
    }

    call(x, y, myElement) {
        const position = this.getJoysticPosition(x, y)
        if (position != "") {
            const command = this.getCommand(position, myElement)
            this.sendCommand("keypress", command)
        }
    }

    getJoysticPosition(x, y) {
        if (y > 90) {
            return "DOWN"
        }
        if (y < -90) {
            return "UP"
        }

        if (x < -90) {
            return "LEFT"
        }

        if (x > 90) {
            return "RIGHT"
        }
        return ""
    }

    getCommand(position, myElement) {
        if (myElement.classList.contains("right")) {
            return this.right[position]
        }
        return this.left[position]
    }

}


function createHammerControl(psp, stage, myElement) {
    let xCenter = 0;
    let yCenter = 0;
    let commander = new JoystickCommand()
    var mc = new Hammer(myElement);
    mc.add(new Hammer.Pan({threshold: 0, pointers: 0}));
    mc.on("panstart", function (ev) {
        xCenter = psp.x;
        yCenter = psp.y;
        psp.alpha = 0.5;

        stage.update();
    });

    // listen to events...
    mc.on("panmove", function (ev) {
        const coords = calculateCoords(ev.angle, ev.distance);
        commander.call(coords.x, coords.y, myElement)

        psp.x = coords.x;
        psp.y = coords.y;
        psp.alpha = 0.5;

        stage.update();
    });

    mc.on("panend", function (ev) {
        psp.alpha = 0.25;
        createjs.Tween.get(psp).to({x: xCenter, y: yCenter}, 750, createjs.Ease.elasticOut);
        commander.sendCommand("release", "")
    });
    return {xCenter, yCenter};
}

function init() {
    createJoystick('joystick-left')
    createJoystick('joystick-right')
}

function createJoystick(myElementId) {
    var stage = new createjs.Stage(myElementId);

    var psp = new createjs.Shape();
    psp.graphics.beginFill('#333333').drawCircle(150, 150, 50);

    psp.alpha = 0.25;

    var vertical = new createjs.Shape();
    var horizontal = new createjs.Shape();

    stage.addChild(psp);
    stage.addChild(vertical);
    stage.addChild(horizontal);
    createjs.Ticker.framerate = 60;
    createjs.Ticker.addEventListener('tick', stage);
    stage.update();
    var myElement = document.getElementById(myElementId);
    createHammerControl(psp, stage, myElement);
}

function calculateCoords(angle, distance) {
    const coords = {};
    distance = Math.min(distance, 100);
    const rads = (angle * Math.PI) / 180.0;

    coords.x = distance * Math.cos(rads);
    coords.y = distance * Math.sin(rads);

    return coords;
}

