function createHammerControl(psp, stage, myElement) {
    let xCenter = 0;
    let yCenter = 0;
    // create a simple instance
    // by default, it only adds horizontal recognizers
    var mc = new Hammer(myElement);

    mc.on("panstart", function (ev) {
        xCenter = psp.x;
        yCenter = psp.y;
        psp.alpha = 0.5;

        stage.update();
    });

    // listen to events...
    mc.on("panmove", function (ev) {
        var x = (ev.center.x - myElement.offsetLeft - 150);
        var y = (ev.center.y - myElement.offsetTop - 150);
        console.log(x, y)

        var coords = calculateCoords(ev.angle, ev.distance);
        psp.x = coords.x;
        psp.y = coords.y;
        psp.alpha = 0.5;

        stage.update();
    });

    mc.on("panend", function (ev) {
        psp.alpha = 0.25;
        createjs.Tween.get(psp).to({x: xCenter, y: yCenter}, 750, createjs.Ease.elasticOut);
    });
    return {xCenter, yCenter};
}

function init() {
    createJoystick('joystick-left')
    createJoystick('joystick-right')
}

function createJoystick(myElementId) {
    // easal stuff goes hur
    var xCenter = 150;
    var yCenter = 150;
    var stage = new createjs.Stage(myElementId);

    var psp = new createjs.Shape();
    psp.graphics.beginFill('#333333').drawCircle(xCenter, yCenter, 50);

    psp.alpha = 0.25;

    var vertical = new createjs.Shape();
    var horizontal = new createjs.Shape();
    vertical.graphics.beginFill('#ff4d4d').drawRect(150, 0, 2, 300);
    horizontal.graphics.beginFill('#ff4d4d').drawRect(0, 150, 300, 2);

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
    var coords = {};
    distance = Math.min(distance, 100);
    var rads = (angle * Math.PI) / 180.0;

    coords.x = distance * Math.cos(rads);
    coords.y = distance * Math.sin(rads);

    return coords;
}

