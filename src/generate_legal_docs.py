import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
Task 1 - Tạo văn bản pháp luật lao động mẫu (PDF)
"""
from pathlib import Path
from fpdf import FPDF
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class LaborLawPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 8, "BO LAO DONG VIET NAM", ln=True, align="C")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Trang {self.page_no()}", align="C")


def create_bo_luat_lao_dong_2019():
    """Tạo file PDF Bộ luật Lao động 2019 (tóm tắt các điều quan trọng)"""
    pdf = LaborLawPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Tiêu đề
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "BO LUAT LAO DONG 2019", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Luat so 45/2019/QH14 ngay 20/11/2019", ln=True, align="C")
    pdf.ln(8)

    # Mục 1: Thử việc
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "CHUONG I - THU VIEC", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 25. Thoi gian thu viec
1. Thoi gian thu viec theo thoa thuan khong qua 02 ngay lam viec tuan den it nhat 01 lan trong 
tho gian 180 ngay, tru nhung truong hop sau day:
   a) Nhung cong viec co dau hieu nang ne, doc hai, nguy hiem;
   b) Nhung cong viec yeu cau nguoi thu viec phai co trinh do chuyen mon cao, ky nang 
      chuyen doi cao.
2. Nguoi lao dong duoc tra luong thu viec it nhat bang 85% muc luong cua viec chinh thuc.

Dieu 26. Cham dut thoi gian thu viec
1. Nguoi dung lao dong va nguoi lao dong co quyen chau dut thoi gian thu viec truoc thoi han 
   khi ket thuc thoi gian thu viec theo thoa thuan.
2. Het thoi gian thu viec, nguoi dung lao dong phai ban giao cong viec va nhuan chung 
   cho nguoi lao dong.
"""
    pdf.multi_cell(0, 5, content)

    # Mục 2: Thời giờ làm việc
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "CHUONG II - THOI GIO LAM VIEC", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 33. Thoi gian lam viec binh thuong
1. Thoi gian lam viec binh thuong hang ngay khong qua 08 gio trong 01 ngay doi voi nguoi 
   lam viec theo thoi gian quy dinh tai khoan 1 diem a khoan 1 Dieu 54 cua Bo luat nay.
2. Tong thoi gian lam viec binh thuong trong 01 tuan it nhat 24 gio va khong qua 48 gio.

Dieu 35. Lam them gio
1. Nguoi dung lao dong co quyen yeu cau nguoi lao dong lam them gio khi co su dong y cua 
   nguoi lao dong trong truong hop sau:
   a) Do nhu cau san xuat, kinh doanh;
   b) Do luc luong chap cnhan, khac phuc hau qua do thien tai, hoa hoan, dun.
2. Thoi gian lam them gio khong qua 50% so gio lam viec binh thuong trong 01 ngay; trong 
   truong hop ap dung quy dinh tai diem b khoan 1 Dieu 106 cua Bo luat nay, 
   thoi gian lam them gio khong qua 300% so gio lam viec binh thuong.
"""
    pdf.multi_cell(0, 5, content)

    # Mục 3: Nghỉ phép
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "CHUONG III - NGHI PHEP", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 111. Nghi phep hang nam
1. Nguoi lao dong lam viec tu duoi 12 thang duoc nghi phep huong luong theo thoi gian 
   thuc te lam viec.
2. Nguoi lao dong lam viec tu 12 thang tro len duoc nghi phep huong luong, moi nam 
   it nhat 12 ngay lam viec; doi voi nguoi lam viec nghengach, lam viec nang, doc hai, 
   nguy hiem thi it nhat 14 ngay lam viec va nguoi lam viec la nguoi khuyet tat.
3. Nguoi lao dung co tra luong cho nguoi lao dong nghi phep, moi ngay nghi phep huong 
   luong bang muc luong theo thoa thuan trong hop dong lao dong.
"""
    pdf.multi_cell(0, 5, content)

    # Mục 4: Hợp đồng lao động
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "CHUONG IV - HOP DONG LAO DONG", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 13. Hop dong lao dong
1. Hop dong lao dong la su thoa thuan giua nguoi lao dong va nguoi dung lao dong vei 
   noi dung sau:
   a) Viec lam, dia diem lam viec, thoi han lam viec, thoi gian lam viec, thoi gian nghi 
      phep, thoi gian nghi giua ca;
   b) Muc luong, hinh thuc tra luong, thoi han tra luong, phu cap, che do va phuc loi khac;
   c) Doi voi nguoi lao dong: ho va ten, ngay thang nam sinh, gioi tinh, dia chi, so 
      CCCD, so BHXH, trinh do chuyen mon.
2. Trong truong hop hop dong lao dong giao ket khong dung voi quy dinh tai Dieu nay thi 
   ap dung thoi han, noi dung giao ket theo quy dinh cua phap luat tuong ung.
"""
    pdf.multi_cell(0, 5, content)

    # Mục 5: Chấm dứt HĐLĐ
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "CHUONG V - CHAM DUT HOP DONG LAO DONG", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 34. Nguyen tac chung ve cham dut hop dong lao dong
Viec cham dut hop dong lao dong phai thuc hien trong truong hop, thu tu va thoi han 
duoc quy dinh cua Bo luat nay.

Dieu 35. Cac truong hop cham dut hop dong lao dong
1. Het thoi han hop dong lao dong.
2. Hoan thanh cong viec theo hop dong lao dong.
3. Nguoi lao dong va nguoi dung lao dong thoa thuan ket thuc hop dong lao dong.
4. Nguoi lao dong bi tuyc nhuong khi co mot trong cac truong hop quy dinh tai Dieu 40 
   cua Bo luat nay.
5. Nguoi dung lao dong chat theo quy dinh tai Dieu 42 cua Bo luat nay.
6. Hop dong lao dong bi tuyc chet do dac thu ve nguoi lao dong hoac nguoi dung lao dong.

Dieu 45. Thong bao ve viec cham dut hop dong lao dong
1. Nguoi dung lao dong phai thong bao bang van ban cho nguoi lao dong ve viec cham dut 
   hop dong lao dong it nhat 30 ngay truong truoc trong truong hop quy dinh tai cac diem 
   a, c, d va e khoan 1 Dieu 34 cua Bo luat nay.
"""
    pdf.multi_cell(0, 5, content)

    output_path = DATA_DIR / "bo-luat-lao-dong-2019.pdf"
    pdf.output(str(output_path))
    print(f"[OK] Created: bo-luat-lao-dong-2019.pdf")


def create_nghi_dinh_145_2020():
    """Tạo file PDF Nghị định 145/2020/NĐ-CP"""
    pdf = LaborLawPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "NGHI DINH 145/2020/ND-CP", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Huong dan thi hanh Bo luat Lao dong", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "PHAN I: QUY DINH VE THU VIEC", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 1. Thoi gian thu viec
1. Thoi gian thu viec thoa thuan trong hop dong thu viec khong qua 02 ngay lam viec tuan, 
   it nhat 01 lan trong tho gian 180 ngay, tru nhung truong hop sau:
   a) Cong viec nang, doc hai, nguy hiem;
   b) Cong viec yeu cau trinh do chuyen mon cao, ky nang chuyen doi cao.
2. Muc luong thu viec it nhat bang 85% muc luong cua viec chinh thuc.

Dieu 2. Tra luong thu viec
1. Muc luong thu viec = Muc luong chinh thuc cua viec tuong ung x 85%
2. Nguoi dung lao dong tra luong thu viec theo thoi gian thuc te lam viec.
"""
    pdf.multi_cell(0, 5, content)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "PHAN II: LUONG VA PHUONG THUC TRA LUONG", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 3. Cac khoan phu cap
1. Cac khoan phu cap bao gom:
   a) Phu cap chuc vu;
   b) Phu cap phuc vu;
   c) Phu cap thanh toan lan;
   d) Phu cap di lam xa;
   e) Phu cap khac.
2. Muc phu cap do nguoi dung lao dong va nguoi lao dong thoa thuan.

Dieu 4. Tra luong
1. Nguoi dung lao dong tra luong cho nguoi lao dong it nhat 01 lan/thang hoac chia 
   theo ky tra luong.
2. Phuong thuc tra luong do nguoi dung lao dong va nguoi lao dong thoa thuan.
"""
    pdf.multi_cell(0, 5, content)

    output_path = DATA_DIR / "nghi-dinh-145-2020-nd-cp.pdf"
    pdf.output(str(output_path))
    print(f"[OK] Created: nghi-dinh-145-2020-nd-cp.pdf")


def create_thong_tu_10_2020():
    """Tạo file PDF Thông tư 10/2020/TT-BLĐTBXH"""
    pdf = LaborLawPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "THONG TU 10/2020/TT-BLDTBXH", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Huong dan mot so noi dung ve hop dong lao dong", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "CHUONG I: HO SO KY KET HOP DONG LAO DONG", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 3. Ho so ky ket hop dong lao dong
1. Nguoi lao dong khi ky ket hop dong lao dong gui nguoi dung lao dong cac giay to sau:
   a) Chung minh nhan dan (CMND) hoac The can cuoc cong dan (CCCD) hoac Ho chieu;
   b) So so BHXH (neu co);
   c) Bang, chung chi, chung nhan, phu cap chuyen mon (neu co yeu cau).
2. Nguoi dung lao dong khong duoc yeu cau nguoi lao dong cung cap giay to khong lien 
   quan den viec thuc hien hop dong lao dong.

Dieu 4. Noi dung hop dong lao dong
1. Hop dong lao dong phai co cac noi dung chinh:
   a) Viec lam va dia diem lam viec cu the;
   b) Thoi han lam viec (duoi 01 thang, 01 thang tro len, 01 nam tro len hoac khong 
      xac dinh thoi han);
   c) Thoi gian lam viec va thoi gian nghi phep hang nam;
   d) Muc luong, phu cap, che do phuc loi;
   e) Quyen va nghia vu cua hai ben.
"""
    pdf.multi_cell(0, 5, content)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "CHUONG II: THOA THUAN VE NOI DUNG TAM NGUNG THUC HIEN HDLD", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Dieu 5. Cac truong hop tam ngung thuc hien hop dong lao dong
1. Nguoi lao dong va nguoi dung lao dong co the thoa thuan tam ngung thuc hien hop 
   dong lao dong trong cac truong hop:
   a) Nguoi lao dong phai tam ngung viec do tai nan lao dong, benh ngan dai;
   b) Nguoi dung lao dong tam ngung san xuat, kinh doanh;
   c) Do nhu cau ca nhan cua nguoi lao dong.
2. Thoi gian tam ngung thuc hien hop dong lao dong khong tinh vao thoi han hop dong lao dong.
"""
    pdf.multi_cell(0, 5, content)

    output_path = DATA_DIR / "thong-tu-10-2020-tt-bldtbxh.pdf"
    pdf.output(str(output_path))
    print(f"[OK] Created: thong-tu-10-2020-tt-bldtbxh.pdf")


def create_co_quan_lao_dong():
    """Tạo file PDF Quy chế dành cho người lao động mới"""
    pdf = LaborLawPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "QUY DINH VE CHE DO LAM VIEC", ln=True, align="C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 6, "Danh cho nhan vien moi", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "I. GIOI THIEU", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
Cong ty ABC gioi thieu quy dinh ve che do lam viec, luong, thu viec, nghi phep va cac 
che do phuc loi khac cho nhan vien.
"""
    pdf.multi_cell(0, 5, content)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "II. GIO LAM VIEC", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
1. Gio lam viec chinh thuc: 8h30 - 17h30, thu Hai - Thu Sau
2. Nghi trua: 12h00 - 13h00
3. Nghi cuoi tuan: Thu Bay, Chu Nhat
4. Di tre/ve som: 
   - Di tre hon 15 phut: Bị tru 15 phut cong
   - Ve som hon 30 phut: Khong tinh cong

III. CHE DO LUONG
1. Luong NET: Tong luong - (BHXH + Thue TNCN)
2. Thue TNCN: Theo bang tien luyen phuong phap khoan luy tien.
3. Thanh toan luong: Ngay 10 thang tiep theo (chuyen khoan)
"""
    pdf.multi_cell(0, 5, content)

    pdf.add_page()
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "IV. THU VIEC", ln=True)
    pdf.set_font("Helvetica", "", 10)
    content = """
1. Thoi gian thu viec: 02 thang (co the giam con 01 thang neu duoc danh gia tot)
2. Muc luong thu viec: 85% luong chinh thuc
3. Quyen loi trong thoi gian thu viec:
   - Duoc tham gia bao hiem xa hoi, bao hiem y
   - Duoc nghi phep theo ty le 1 ngay/thang
   - Duoc dao tao noi bo

V. NGHI PHEP HANG NAM
1. 12 ngay phep nam (tinh theo nam tai chinh)
2. Co the chuyen doi thanh tien: 50% so ngay phep con lai
3. Phep nam tinh theo thoi gian thuc te lam viec trong nam
"""
    pdf.multi_cell(0, 5, content)

    output_path = DATA_DIR / "quy-dinh-noi-bo-cong-ty.pdf"
    pdf.output(str(output_path))
    print(f"[OK] Created: quy-dinh-noi-bo-cong-ty.pdf")


if __name__ == "__main__":
    print("=" * 50)
    print("Task 1: Creating Labor Law PDFs")
    print("=" * 50)
    create_bo_luat_lao_dong_2019()
    create_nghi_dinh_145_2020()
    create_thong_tu_10_2020()
    create_co_quan_lao_dong()
    print("\nDone! Created 4 PDF files in data/landing/legal/")
