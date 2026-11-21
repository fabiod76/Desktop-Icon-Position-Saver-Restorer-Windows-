import ctypes, json, sys
from ctypes import wintypes as w

user32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
LVM_GETITEMCOUNT, LVM_SETITEMPOSITION = 0x1004, 0x100F
LVM_GETITEMPOSITION, LVM_GETITEMTEXTW = 0x1010, 0x1073
PROCESS_ALL, MEM_COMMIT_RESERVE, MEM_RELEASE, PAGE_RW = 0x1F0FFF, 0x3000, 0x8000, 4
FILE = "icone.json"

class LVITEMW(ctypes.Structure):
    _fields_ = [("mask", w.UINT), ("iItem", ctypes.c_int), ("iSubItem", ctypes.c_int),
                ("state", w.UINT), ("stateMask", w.UINT), ("pszText", ctypes.c_void_p),
                ("cchTextMax", ctypes.c_int), ("iImage", ctypes.c_int), ("lParam", w.LPARAM)]

for f in (user32.FindWindowW, user32.FindWindowExW, user32.SendMessageW):
    f.restype = ctypes.c_void_p
user32.SendMessageW.argtypes = [w.HWND, w.UINT, w.WPARAM, w.LPARAM]
user32.FindWindowExW.argtypes = [w.HWND, w.HWND, w.LPCWSTR, w.LPCWSTR]
k32.VirtualAllocEx.restype = ctypes.c_void_p
k32.VirtualAllocEx.argtypes = [w.HANDLE, ctypes.c_void_p, ctypes.c_size_t, w.DWORD, w.DWORD]
k32.VirtualFreeEx.argtypes = [w.HANDLE, ctypes.c_void_p, ctypes.c_size_t, w.DWORD]
k32.ReadProcessMemory.argtypes = [w.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p]
k32.WriteProcessMemory.argtypes = [w.HANDLE, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_void_p]
k32.OpenProcess.restype = w.HANDLE

def find_listview():
    # Il desktop sta sotto Progman oppure sotto un WorkerW
    defview = user32.FindWindowExW(user32.FindWindowW("Progman", None), None, "SHELLDLL_DefView", None)
    if not defview:
        ww = None
        while True:
            ww = user32.FindWindowExW(None, ww, "WorkerW", None)
            if not ww: break
            defview = user32.FindWindowExW(ww, None, "SHELLDLL_DefView", None)
            if defview: break
    return user32.FindWindowExW(defview, None, "SysListView32", None)

def icons():
    lv = find_listview()
    pid = w.DWORD()
    user32.GetWindowThreadProcessId(w.HWND(lv), ctypes.byref(pid))
    proc = k32.OpenProcess(PROCESS_ALL, False, pid.value)
    mem = k32.VirtualAllocEx(proc, None, 4096, MEM_COMMIT_RESERVE, PAGE_RW)
    try:
        n = user32.SendMessageW(lv, LVM_GETITEMCOUNT, 0, 0)
        for i in range(n):
            # nome
            item = LVITEMW(); item.mask = 1; item.pszText = mem + 512; item.cchTextMax = 260
            k32.WriteProcessMemory(proc, mem, ctypes.byref(item), ctypes.sizeof(item), None)
            user32.SendMessageW(lv, LVM_GETITEMTEXTW, i, mem)
            buf = ctypes.create_unicode_buffer(260)
            k32.ReadProcessMemory(proc, mem + 512, buf, 520, None)
            # posizione
            user32.SendMessageW(lv, LVM_GETITEMPOSITION, i, mem + 2048)
            pt = w.POINT()
            k32.ReadProcessMemory(proc, mem + 2048, ctypes.byref(pt), ctypes.sizeof(pt), None)
            yield lv, i, buf.value, pt.x, pt.y
    finally:
        k32.VirtualFreeEx(proc, mem, 0, MEM_RELEASE)
        k32.CloseHandle(proc)

def salva():
    data = {name: (x, y) for _, _, name, x, y in icons()}
    json.dump(data, open(FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"Salvate {len(data)} icone")

def ripristina():
    data = json.load(open(FILE, encoding="utf-8"))
    ok = 0
    for lv, i, name, _, _ in icons():
        if name in data:
            x, y = data[name]
            user32.SendMessageW(lv, LVM_SETITEMPOSITION, i, (y << 16) | (x & 0xFFFF))
            ok += 1
    print(f"Riposizionate {ok} icone")

if __name__ == "__main__":
    {"s": salva, "salva": salva, "r": ripristina, "ripristina": ripristina}[sys.argv[1]]()
