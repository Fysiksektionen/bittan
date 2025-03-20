import { useEffect, useRef, useState } from "react";
import QrScanner from "qr-scanner";
const TicketScanner = () => {
    const scanner = useRef();
    const videoEl = useRef(null);
    const qrBoxEl = useRef(null);
    const [qrOn, setQrOn] = useState(true);
    const [scannedResult, setScannedResult] = useState("");

    const onSuccess = (result) => {
        console.log(result);
        setScannedResult(result?.data);
        scanner?.current?.stop();
    }

    const onFail = (err) => {
        console.log(err)
    }

    useEffect(() => {
        if(videoEl?.current && !scanner.current) {
            scanner.current = new QrScanner(videoEl?.current, onSuccess, {
                onDecodeError: onFail,
                preferredCamera: "environment",
                highlightScanRegion: true,
                highlightCodeOutline: true,
                overlay: qrBoxEl?.current || undefined,
            });

            scanner?.current
                ?.start()
                .then(() => setQrOn(true))
                .catch((err) => {
                    if(err) setQrOn(false);
                });
        }

        return () => {
            if(!videoEl?.current) {
                scanner?.current?.stop()
            }
        };
    }, []);



    return(
        <div className="qr-reader">
             <video style={{width: "70wv", height: "auto"}} ref={videoEl}></video>
            {scannedResult && (
                <p
                    style={{
                        position: "absolute",
                        top: 0,
                        left: 0,
                        zIndex: 99999,
                        color:"white",
                    }}
                >
                    {scannedResult}
                </p>
            )}
        </div>
    );
};

export default TicketScanner;
