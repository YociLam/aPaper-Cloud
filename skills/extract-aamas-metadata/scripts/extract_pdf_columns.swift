import AppKit
import PDFKit
import Vision
let document = PDFDocument(url: URL(fileURLWithPath: CommandLine.arguments[1]))!
for index in 0..<min(2, document.pageCount) {
    let image = document.page(at:index)!.thumbnail(of:NSSize(width:2000,height:2800),for:.mediaBox)
    let cg = image.cgImage(forProposedRect:nil,context:nil,hints:nil)!
    for x in [0.03,0.51] {
        let request = VNRecognizeTextRequest()
        request.recognitionLevel = .accurate
        request.recognitionLanguages = ["en-US"]
        request.usesLanguageCorrection = false
        request.regionOfInterest = CGRect(x:x,y:0.04,width:0.46,height:0.92)
        try VNImageRequestHandler(cgImage:cg).perform([request])
        for observation in request.results ?? [] { print(observation.topCandidates(1).first?.string ?? "") }
    }
}
