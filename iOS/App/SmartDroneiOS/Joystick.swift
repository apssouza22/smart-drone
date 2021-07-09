//
//  Joystick.swift
//  SmartDroneiOS
//
//  Created by MinJeong Kim on 07/07/2021.
//

import UIKit

class Joystick: UIView {
    enum Direction: String {
        case up = "u"
        case left = "l"
        case down = "d"
        case right = "r"
        case release = "x"
    }
    private var id: String!
    private var resultCallback: ((_ id: String, Direction) -> Void)?
    private var thread: Thread!
    private var normalizedPoint: CGPoint?
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setup()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setup()
    }
    
    private func setup() {
        self.layer.cornerRadius = self.frame.height * 0.5
        self.backgroundColor = .green
        self.alpha = 0.5
    }
    
    public func start(id: String, _ block: ((_ id: String, Direction) -> Void)?) {
        self.id = id
        resultCallback = block
        thread = Thread.init(target: self, selector: #selector(tracking), object: nil)
        thread.start()
    }
    
    public func stop() {
        resultCallback = nil
        if thread != nil {
            thread.cancel()
            thread = nil
        }
    }
    
    override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
        if let currentTouch = touches.first {
            let currentPoint = currentTouch.location(in: self)
            let point = CGPoint(x: currentPoint.x / self.frame.size.width, y: currentPoint.y / self.frame.size.height)
            normalizedPoint = CGPoint(x: (point.x - 0.5) * 2, y: (-point.y + 0.5) * 2)
        }
    }
    
    override func touchesMoved(_ touches: Set<UITouch>, with event: UIEvent?) {
        if let currentTouch = touches.first {
            let currentPoint = currentTouch.location(in: self)
            let point = CGPoint(x: currentPoint.x / self.frame.size.width, y: currentPoint.y / self.frame.size.height)
            normalizedPoint = CGPoint(x: (point.x - 0.5) * 2, y: (-point.y + 0.5) * 2)
        }
    }
    
    override func touchesEnded(_ touches: Set<UITouch>, with event: UIEvent?) {
        normalizedPoint = nil
        if let resultCallback = resultCallback {
            resultCallback(self.id, .release)
        }
    }

    @objc private func tracking() {
        while true {
            if let normalizedPoint = normalizedPoint,
               let resultCallback = resultCallback {
                if normalizedPoint.x > -1 && normalizedPoint.x < 1 &&
                    normalizedPoint.y > -1 && normalizedPoint.y < 1 {
                    let x = normalizedPoint.x
                    let y = normalizedPoint.y
                    if x > y && x > -y {
                        resultCallback(self.id, .right)
                    } else if x < y && x > -y {
                        resultCallback(self.id, .up)
                    } else if (x > y && x < -y) {
                        resultCallback(self.id, .down)
                    } else {
                        resultCallback(self.id, .left)
                    }
                }
            }
            usleep(100)
        }
    }
    
}
