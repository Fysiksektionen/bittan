import { useEffect, useRef, useState } from "react";

import QrScanner from "qr-scanner";
const TicketScanner = () => {
    const scanner = useRef<QrScanner>();
    const videoEl = useRef<HTMLVideoElement>(null);
    const qrBoxEl = useRef<HTMLDivElement>(null);
    const [qrOn, setQrOn] = useState<boolean>(true);
    const [scannedResult, setScannedResult] = useState<string | undefined>("");

    const onSuccess = (result: QrScanner.ScanResult) => {
        console.log(result);
        console.log('wazzup');
        setScannedResult(result?.data);
        scanner?.current?.stop();
        window.location.replace(result?.data);
    }

    const onFail = (err: string | Error) => {
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
             <video ref={videoEl}></video>
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