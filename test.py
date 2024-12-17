import paddle

print("Paddle version:", paddle.__version__)
print("Is GPU available:", paddle.is_compiled_with_cuda())
print("CUDA available devices:", paddle.device.cuda.device_count())