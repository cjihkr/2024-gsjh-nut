from gnuradio import gr, blocks, analog
import osmosdr
from threading import Timer
import sys

class HackRFJammingFlowgraph(gr.top_block):
    def __init__(self):
        gr.top_block.__init__(self, "HackRF Jamming Flowgraph")

        # 설정 변수
        self.samp_rate = 20e6  # 샘플 레이트: 20 MHz
        self.center_freq_1 = 2.465e9  # 첫 번째 주파수: 2.46 GHz
        self.center_freq_2 = 2.46e9  # 두 번째 주파수: 2.45 GHz
        self.current_freq = self.center_freq_1  # 초기 주파수 설정
        self.noise_amplitude = 100  # 노이즈 신호의 진폭

        # 블록 정의
        # Gaussian Noise Source
        self.noise_source = analog.noise_source_c(analog.GR_GAUSSIAN, self.noise_amplitude, 0)

        # Throttle 블록
        self.throttle = blocks.throttle(gr.sizeof_gr_complex, self.samp_rate, True)

        # HackRF Sink (osmosdr)
        self.osmo_sink = osmosdr.sink(args="hackrf=117ca7")
        self.osmo_sink.set_sample_rate(self.samp_rate)
        self.osmo_sink.set_center_freq(self.current_freq, 0)  # 초기 중심 주파수 설정
        self.osmo_sink.set_freq_corr(0, 0)  # 주파수 보정
        self.osmo_sink.set_gain(14, 0)  # RF Gain 설정
        self.osmo_sink.set_if_gain(62, 0)  # IF Gain 설정
        self.osmo_sink.set_bb_gain(0, 0)  # BB Gain 설정
        self.osmo_sink.set_antenna("", 0)  # 안테나 설정 (기본값)
        self.osmo_sink.set_bandwidth(20e6, 0)  # 대역폭 설정: 20 MHz

        # 블록 연결
        self.connect(self.noise_source, self.throttle)
        self.connect(self.throttle, self.osmo_sink)

        # 주파수 전환 타이머
        self.timer_interval = 2  # 주파수 전환 주기 (초)
        self.timer = Timer(self.timer_interval, self.toggle_frequency)
        self.timer.start()

    def toggle_frequency(self):
        """중심 주파수를 전환하는 함수"""
        self.current_freq = self.center_freq_2 if self.current_freq == self.center_freq_1 else self.center_freq_1
        self.osmo_sink.set_center_freq(self.current_freq, 0)
        print(f"중심 주파수 전환: {self.current_freq / 1e6} MHz")

        # 타이머 재설정
        self.timer = Timer(self.timer_interval, self.toggle_frequency)
        self.timer.start()

    def stop_timers(self):
        """타이머를 중지"""
        self.timer.cancel()

# 실행
if __name__ == "__main__":
    try:
        tb = HackRFJammingFlowgraph()
        tb.start()
        print("HackRF Jamming Flowgraph 시작")
        input("종료하려면 Enter를 누르세요...\n")
    finally:
        tb.stop_timers()
        tb.stop()
        tb.wait()
        print("HackRF Jamming Flowgraph 종료")
