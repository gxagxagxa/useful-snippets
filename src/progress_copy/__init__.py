import os
from enum import Enum
from pathlib import Path
from time import time as _time
from typing import Optional, Callable


class ProgressCopyFile():
    class CopyEnum(Enum):
        READY = 'ready'
        PROGRESSING = 'progressing'
        SUCCESS = 'success'
        FAIL = 'fail'
        SKIP = 'skip'

    __slots__ = ('src', 'dst', 'overwrite', 'mkdirs',
                 'chunk_size', 'progress_callback', 'finish_callback',
                 'update_interval', '__status', 'start_time', 'end_time')

    def __init__(self, src: Path, dst: Path,
                 overwrite: bool = False,
                 mkdirs: bool = True,
                 chunk_size: int = 1024 * 1024,
                 progress_callback: Optional[Callable] = None,
                 finish_callback: Optional[Callable] = None,
                 update_interval: float = 1) -> None:
        super().__init__()
        self.src: Path = Path(src)
        self.dst: Path = Path(dst)
        self.overwrite: bool = overwrite
        self.mkdirs: bool = mkdirs
        self.chunk_size: int = chunk_size
        self.progress_callback: Optional[Callable] = progress_callback
        self.finish_callback: Optional[Callable] = finish_callback
        self.update_interval: float = update_interval
        self.__status: ProgressCopyFile.CopyEnum = ProgressCopyFile.CopyEnum.READY
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

    @property
    def status(self):
        return self.__status

    def execute(self):
        if self.__status is not ProgressCopyFile.CopyEnum.READY:
            return

        if self.dst.exists() and not self.overwrite:
            self.__status = ProgressCopyFile.CopyEnum.SKIP
            return

        with open(self.src, 'rb') as src_file:
            if not self.dst.parent.exists() and self.mkdirs:
                self.dst.parent.mkdir(mode=0o755, parents=True, exist_ok=True)

            with open(self.dst, 'wb') as dst_file:
                _current = 0
                _total = os.fstat(src_file.fileno()).st_size
                _remaining = _total - _current
                _chuck_size = self.chunk_size
                _src_fiile_read = src_file.read
                _dst_flie_write = dst_file.write
                self.__status = ProgressCopyFile.CopyEnum.PROGRESSING
                self.start_time = _start_time = _time()

                if self.progress_callback is None:
                    while _remaining > 0:
                        _data = _src_fiile_read(_chuck_size)
                        _dst_flie_write(_data)
                        _data_length = len(_data)
                        _current += _data_length
                        _remaining -= _data_length
                else:
                    _last_call = _start_time
                    _update_interval = self.update_interval
                    _progress_callback = self.progress_callback
                    while _remaining > 0:
                        _data = _src_fiile_read(_chuck_size)
                        _dst_flie_write(_data)
                        _data_length = len(_data)
                        _current += _data_length
                        _remaining -= _data_length
                        _now = _time()
                        if _now - _last_call > _update_interval:
                            _progress_callback(_current, _remaining, _total, _start_time, _now)
                            _last_call = _time()

                self.end_time = _time()
                if self.progress_callback:
                    self.progress_callback(_current, _remaining, _total, self.start_time, self.end_time)
                self.__status = ProgressCopyFile.CopyEnum.SUCCESS

        if self.finish_callback:
            self.finish_callback(self.src, self.dst, self.start_time, self.end_time)


if __name__ == '__main__':
    src = '/Volumes/DATA/softwawre/pr_2020/Adobe_Premiere_Pro_2020_14.0.0.571_20191023.dmg'
    dst = '/Users/andyguo/Desktop/copyed.mov'


    def callback(current, remaining, total, start, now):
        percentage = current / total * 100.0
        speed = current / (now - start)
        print(f'{percentage :.2f}% of {total / 1024 / 1024:.3f} MB, '
              f'speed = {speed / 1024 / 1024 :.3f} MB/s, '
              f'ETA = {remaining / speed: .1f} seconds')


    copy_object = ProgressCopyFile(src, dst, progress_callback=callback, overwrite=True, update_interval=0.5)
    start = _time()
    print(_time())
    copy_object.execute()
    print(_time() - start)
