//
//  ViewController.swift
//  SmartDroneiOS
//
//  Created by MinJeong Kim on 07/07/2021.
//

import UIKit
import Network
import SwiftSocket

class ViewController: UIViewController {
    @IBOutlet var infoLabel: UILabel!
    @IBOutlet var imageView: UIImageView!
    
    enum State {
        case start
        case ready
        case connected
        case failed(message: String)
    }
    
    var address: String!
    let port: Int32 = 8245
    var server: TCPServer!
    var client: TCPClient!
    
    var state: State? {
        didSet {
            switch state {
            case .start:
                address = UIDevice.current.ipv4(for: .wifi)!
                guard address != nil else {
                    changeState(to: .failed(message: "Can not get the network info"))
                    return
                }
                server = TCPServer(address: address, port: port)
                switch server.listen() {
                case .success:
                    changeState(to: .ready)
                case .failure(let error):
                    changeState(to: .failed(message: "Failed server.listen: \(error.localizedDescription)"))
                }
            case .ready:
                showInfoMessage("Connect to\n\(self.address!):\(self.port)\nto Start")
                DispatchQueue.global(qos: .background).async { [weak self] in
                    guard let self = self else { return }
                    while self.client == nil {
                        self.client = self.server.accept()
                    }
                    self.changeState(to: .connected)
                }
            case .connected:
                DispatchQueue.global(qos: .background).async { [weak self] in
                    guard let self = self else { return }
                    while self.client != nil {
                        guard
                            let sizeToReadData = self.client.read(6),
                            let sizeToReadString = String(bytes: sizeToReadData, encoding: .utf8),
                            let sizeToRead = Int(sizeToReadString),
                            sizeToRead > 0 else {
                            self.client = nil
                            break
                        }
                        
                        guard
                            let imageData = self.client.read(sizeToRead),
                            let encodedImageString = String(bytes: imageData, encoding: .utf8),
                            let decodedImage = Data(base64Encoded: encodedImageString),
                            let image = UIImage(data: decodedImage) else {
                            self.client = nil
                            break
                        }
                        
                        self.showImage(image)
                    }
                    self.changeState(to: .ready)
                }
            case .failed(let message):
                showInfoMessage(message)
            case .none:
                break
            }
        }
    }
    
    func changeState(to newState: State) {
        print("App state change to: \(newState)")
        state = newState
        
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            switch self.state {
            case .start:
                self.infoLabel.isHidden = false
                self.imageView.isHidden = true
            case .ready:
                self.infoLabel.isHidden = false
                self.imageView.isHidden = true
            case .connected:
                self.infoLabel.isHidden = true
                self.imageView.isHidden = false
            case .failed(_):
                self.infoLabel.isHidden = false
                self.imageView.isHidden = true
            case .none:
                break
            }
        }
    }
    
    func showInfoMessage(_ message: String) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            self.infoLabel.isHidden = false
            self.infoLabel.text = message
        }
    }
    
    func showImage(_ image: UIImage) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else { return }
            self.imageView.image = nil
            self.imageView.image = image
        }
    }
    
    override func viewDidLoad() {
        changeState(to: .start)
    }
}
