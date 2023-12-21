from flask import Flask, send_file
from escpos.printer import Usb
import escpos.constants

app = Flask(__name__)

@app.route('/')
def index():

    # Create a new instance of the printer object
    printer = Usb(0x4b43, 0x3830, 0, 0x81, 0x03)

    #content to print
    content = 'timestamps nya'
    
    # Set align
    printer.set(align='center')

    #Mulai Print Text Tiketnya
    printer.text('SATPAS POLRES PURWOREJO\n')
        # Set align
    printer.set(align='center')
    printer.text('------------------------\n')
         # Set align
    printer.set(align='center')
    
    printer.text('lay\n')
        # Set align
    printer.set(align='center')
    
    printer.text('------------------------\n')
        # Set align
    printer.set(align='center')
    
    printer.text('ks' 'queue_number\n')
        # Set align
    printer.set(align='center')
    
    #kode QR Code nya
    printer.qr(content, size=16)
        # Set align
    printer.set(align='center')
     
    printer.text('------------------------\n')
        # Set align
    printer.set(align='center')
    
    printer.text('Mohon sabar menunggu\n')
        # Set align
    printer.set(align='center')
    
    printer.text('jam\n')
        # Set align
    printer.set(align='center')

    # Cut the paper
    printer.cut()

    #kirim data jika kertas habis (0)
    #printer.paper_status(0)

    return 'Berhasil di print'
    
if __name__ == '__main__':
    app.run(debug=True)


