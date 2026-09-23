from rtlsdr import RtlSdr
import numpy as np
from utils.sync import handle_rf_sync_frame

class RFListener:
    def __init__(self, freq=915e6, sample_rate=2.4e6):
        self.sdr = RtlSdr()
        self.sdr.sample_rate = sample_rate
        self.sdr.center_freq = freq
        self.sdr.gain = 'auto'

    def listen(self):
        samples = self.sdr.read_samples(256*1024)
        bits = self.demodulate(samples)
        frame = self.decode(bits)
        if frame:
            handle_rf_sync_frame(frame)

    def demodulate(self, samples):
        # Simple FSK / ASK placeholder
        magnitude = np.abs(samples)
        return magnitude > np.mean(magnitude)

    def decode(self, bits):
        try:
            data = bytes(bits.astype(int))
            return data.decode(errors="ignore")
        except:
            return None
