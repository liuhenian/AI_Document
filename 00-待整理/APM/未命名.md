解包动作
sudo unsquashfs img-1659268435_vol-rootfs.ubifs


确认尾部填充
dd if=img-1659268435_vol-rootfs.ubifs bs=1 skip=43346002 2>/dev/null | hexdump -C | head -n 5


执行尾部填充
cat new_image.ubifs tail.bin > final_image.ubifs


比较大小
ls -l final_image.ubifs img-1659268435_vol-rootfs.ubifs