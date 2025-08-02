import qrcode

url = "https://mrgq-2025.vercel.app/"
qr = qrcode.make(url)
qr.save("mrgq2025_qr.png")
