# 1) Overview (Tổng quan)
Website “giới thiệu sản phẩm đơn giản” là một site marketing nhẹ, tập trung trình bày danh mục sản phẩm/dịch vụ, lợi ích, hình ảnh, thông số cơ bản và kêu gọi hành động (CTA) để khách hàng liên hệ/mua hàng. Mục tiêu là tải nhanh, dễ duyệt trên mobile, quản trị nội dung tối thiểu (có thể cấu hình qua JSON/CMS ở giai đoạn sau), phù hợp triển khai bằng React.

# 2) Goals (Mục tiêu)
## 2.1 Business goals
- Tăng số lượng khách hàng tiềm năng (lead) qua form liên hệ / nút gọi / Zalo / email.
- Tăng tỷ lệ chuyển đổi từ người xem → hành động (liên hệ, đặt mua, yêu cầu báo giá).
- Trình bày sản phẩm rõ ràng, tạo niềm tin qua nội dung (giới thiệu doanh nghiệp, chứng nhận, feedback).

## 2.2 Product goals
- Điều hướng đơn giản: người dùng tìm được sản phẩm trong ≤ 3 lần click.
- Trang sản phẩm có đủ thông tin tối thiểu + CTA rõ ràng.
- Tối ưu SEO cơ bản (title/meta, structured content), responsive.

## 2.3 Success metrics (gợi ý đo lường)
- Conversion rate CTA (click “Liên hệ”, “Gọi ngay”, “Nhận báo giá”).
- Số lead hợp lệ/ngày (form submit thành công).
- Thời gian tải (LCP) và điểm Lighthouse (Performance/SEO/Accessibility).

# 3) Audience (Đối tượng người dùng)
## 3.1 Primary users
1) Khách hàng tiềm năng (B2C/B2B)
- Nhu cầu: xem nhanh sản phẩm, giá/thuộc tính cơ bản, hình ảnh, cách mua/liên hệ.
- Hành vi: truy cập từ mobile, lướt nhanh, ưu tiên CTA tức thì.

2) Khách hàng đang cân nhắc (consideration)
- Nhu cầu: so sánh sản phẩm, đọc chi tiết, xem FAQ, chính sách.
- Hành vi: xem nhiều trang, cần điều hướng rõ ràng.

## 3.2 Secondary users
3) Chủ doanh nghiệp/nhân viên marketing (người cập nhật nội dung)
- Nhu cầu: nội dung dễ thay đổi (ít nhất qua file cấu hình/JSON), hình ảnh tối ưu.

# 4) Core User Journeys (Luồng người dùng chính)
## Flow A: Khám phá sản phẩm từ trang chủ → xem chi tiết → liên hệ
1. Người dùng vào Home.
2. Cuộn xem section “Sản phẩm nổi bật” hoặc “Danh mục”.
3. Click một sản phẩm → Product Detail.
4. Xem hình ảnh + thông tin + lợi ích.
5. Click CTA “Liên hệ/Đặt mua” → mở Contact (modal/section/page).
6. Gửi form → nhận thông báo thành công.

## Flow B: Tìm sản phẩm theo danh mục → lọc/tìm → xem chi tiết
1. Vào Products (Danh sách).
2. Chọn danh mục hoặc dùng tìm kiếm.
3. Xem danh sách sản phẩm phù hợp.
4. Click sản phẩm → Product Detail.

## Flow C: Tìm thông tin doanh nghiệp → tăng tin cậy → liên hệ
1. Vào About/Trang giới thiệu.
2. Xem năng lực, điểm mạnh, chứng nhận/đối tác (nếu có).
3. Click CTA “Nhận tư vấn” → Contact.
4. Submit form / click gọi ngay.

## Flow D: Truy cập nhanh qua CTA cố định (mobile)
1. Ở bất kỳ trang nào, người dùng bấm nút nổi “Gọi/Zalo”.
2. Mở ứng dụng gọi điện/Zalo hoặc mở link chat.

# 5) Screen Breakdown (Phân rã màn hình)
## 5.1 Global layout (Dùng chung)
### Header / Navigation
- Logo (click về Home)
- Menu: Home, Sản phẩm, Giới thiệu, Liên hệ (tuỳ scope)
- Nút CTA nổi bật (VD: “Nhận báo giá”)
- Mobile: hamburger menu + drawer

### Footer
- Thông tin công ty: tên, địa chỉ, email, hotline
- Links nhanh: Sản phẩm, Chính sách (nếu có), Liên hệ
- Social icons (FB/Zalo/Instagram/LinkedIn tuỳ)
- Copyright

### Sticky CTA (khuyến nghị)
- Floating buttons: Gọi ngay, Zalo/Chat
- Hiển thị trên mobile; desktop có thể thu gọn

---

## 5.2 Home (Trang chủ)
### Sections chính
1) Hero
- Headline, sub-headline, CTA primary (“Xem sản phẩm”/“Nhận tư vấn”)
- Ảnh/illustration sản phẩm

2) Sản phẩm nổi bật
- Grid cards 6–12 sản phẩm
- Nút “Xem tất cả”

3) Lợi ích/USP
- 3–6 điểm mạnh (icon + text)

4) Quy trình mua hàng / làm việc (tuỳ)
- 3–5 steps

5) Testimonials/Feedback (tuỳ)
- Carousel hoặc list

6) FAQ (tuỳ)
- Accordion

7) Contact CTA
- Banner + nút mở form hoặc scroll tới section liên hệ

### UI elements quan trọng
- ProductCard: ảnh, tên, mô tả ngắn, tag/danh mục, CTA “Xem chi tiết”
- Responsive grid (1 cột mobile, 2–3 tablet, 3–4 desktop)

---

## 5.3 Products List (Danh sách sản phẩm)
### Components
- Toolbar:
  - Search input (theo tên)
  - Category filter (dropdown/chips)
  - Sort (tuỳ): Mới nhất / A–Z
- Product grid/list
- Pagination hoặc “Load more” (tuỳ dữ liệu)

### Empty/Loading/Error states
- Skeleton loading
- Empty: “Không tìm thấy sản phẩm phù hợp”
- Error: “Không thể tải dữ liệu, thử lại”

---

## 5.4 Product Detail (Chi tiết sản phẩm)
### Sections
1) Gallery
- 1 ảnh lớn + thumbnails (hoặc carousel)
2) Product summary
- Tên sản phẩm
- Mô tả ngắn
- Thông số chính (key specs)
- Tags/danh mục
- CTA: “Liên hệ mua hàng / Nhận báo giá”
3) Tabs/Sections nội dung
- Mô tả chi tiết
- Thông số kỹ thuật
- Ứng dụng/Use cases
- Chính sách bảo hành/đổi trả (nếu có)
4) Related products
- 4–8 sản phẩm cùng danh mục
5) Contact mini-section
- Hotline + nút chat nhanh + link form

### UI elements quan trọng
- Breadcrumbs: Home / Sản phẩm / [Tên]
- CTA block “sticky” trên mobile (thanh cố định dưới)

---

## 5.5 About (Giới thiệu) (tuỳ scope tối thiểu)
- Hero giới thiệu
- Mission/values
- Năng lực/điểm mạnh
- Hình ảnh đội ngũ/nhà xưởng (tuỳ)
- CTA liên hệ

---

## 5.6 Contact (Liên hệ)
### Options
- Form liên hệ
- Thông tin liên hệ + bản đồ (Google Maps embed)
- Các kênh nhanh: hotline, email, Zalo

### Form fields (tối thiểu)
- Họ và tên (required)
- Số điện thoại (required)
- Email (optional)
- Nội dung (required)
- Sản phẩm quan tâm (optional, prefill nếu đến từ Product Detail)

### UI states
- Validation inline
- Submit loading
- Success message
- Error message + retry

---

## 5.7 (Optional) Static policy pages
- Chính sách bảo hành/đổi trả
- Chính sách bảo mật

# 6) Functional Requirements (Yêu cầu chức năng) — React frontend ready
## 6.1 Routing & navigation
- FR-01: Hỗ trợ routing các trang: `/`, `/products`, `/products/:slug`, `/about` (optional), `/contact`.
- FR-02: Header menu phản ánh trang đang active.
- FR-03: Breadcrumbs xuất hiện ở Product Detail.

## 6.2 Data model (Frontend-facing)
Có thể bắt đầu với mock data JSON, sau nâng cấp API.

### Product
- id: string
- slug: string (unique)
- name: string
- shortDescription: string
- descriptionHtml or descriptionMarkdown: string
- category: { id, name, slug }
- images: string[] (urls)
- specs: Array<{ label: string; value: string }>
- tags?: string[]
- featured?: boolean
- createdAt?: ISO string (for sorting)

### Site config
- companyName, address, email, hotline
- socialLinks
- zaloLink, phoneLink
- seo defaults (title template, description)

## 6.3 Products listing
- FR-04: Hiển thị danh sách sản phẩm dạng grid.
- FR-05: Search theo `name` (client-side) với debounce (300–500ms).
- FR-06: Filter theo category (1 lựa chọn) và nút reset filter.
- FR-07: Sort tối thiểu: “Mới nhất” (createdAt desc) và “A–Z”.
- FR-08: Mỗi ProductCard click vào mở Product Detail theo slug.
- FR-09: Loading skeleton trong lúc fetch (kể cả mock fetch delay).

## 6.4 Product detail
- FR-10: Load product theo `slug`; nếu không tồn tại → trang 404 (Not Found).
- FR-11: Gallery hỗ trợ xem ảnh lớn, chuyển ảnh bằng thumbnails.
- FR-12: CTA “Liên hệ/ Nhận báo giá”:
  - Mở trang `/contact` và prefill “Sản phẩm quan tâm”
  - Hoặc mở modal contact (chọn 1 cách và nhất quán)
- FR-13: Related products: cùng category, loại trừ sản phẩm hiện tại, tối đa 8.

## 6.5 Contact form
- FR-14: Validate:
  - name required (min 2 ký tự)
  - phone required (regex cơ bản cho VN, chấp nhận 10–11 số; cho phép +84)
  - message required (min 10 ký tự)
  - email nếu có phải đúng định dạng
- FR-15: Submit gửi tới endpoint (placeholder):
  - `POST /api/contact` (hoặc service EmailJS/Formspree tuỳ triển khai)
- FR-16: Hiển thị trạng thái submit (loading/disabled button).
- FR-17: Thành công: reset form, hiển thị message “Đã gửi yêu cầu…”.
- FR-18: Thất bại: hiển thị lỗi và cho phép gửi lại.
- FR-19: Nếu vào Contact từ Product Detail, field “Sản phẩm quan tâm” tự điền và readonly (hoặc editable nhưng có giá trị mặc định).

## 6.6 SEO & meta
- FR-20: Thiết lập `<title>` và meta description theo trang.
- FR-21: Product Detail dùng title: `[Tên sản phẩm] | [Tên công ty]`.
- FR-22: Ảnh có `alt` mô tả (tên sản phẩm + index).

## 6.7 Responsive & accessibility
- FR-23: Responsive breakpoints tối thiểu: mobile (<768), tablet (768–1024), desktop (>1024).
- FR-24: Tất cả nút/inputs có focus state rõ ràng; có `aria-label` cho icon buttons.
- FR-25: Contrast màu đạt tiêu chuẩn cơ bản (WCAG AA khuyến nghị).

## 6.8 Performance & UX quality
- FR-26: Lazy-load ảnh (native `loading="lazy"`), ưu tiên ảnh hero.
- FR-27: Skeletons thay vì spinners cho list.
- FR-28: Không block UI khi filter/search (client-side).

## 6.9 Error handling
- FR-29: Trang 404 cho route không hợp lệ.
- FR-30: Error boundary ở cấp app để bắt lỗi render và hiển thị fallback.

# 7) Acceptance Criteria (Tiêu chí nghiệm thu)
## 7.1 Navigation & pages
- AC-01: Người dùng có thể truy cập Home, Products List, Product Detail, Contact từ menu header trên cả desktop và mobile.
- AC-02: Mobile menu mở/đóng được, click vào link sẽ điều hướng và tự đóng menu.
- AC-03: Route `/products/:slug` hiển thị đúng sản phẩm tương ứng; slug không tồn tại hiển thị 404.

## 7.2 Home
- AC-04: Home hiển thị tối thiểu: Hero + Featured products + CTA liên hệ.
- AC-05: Click “Xem tất cả” tại Featured products điều hướng tới `/products`.

## 7.3 Products List
- AC-06: Danh sách hiển thị đúng số lượng sản phẩm theo dữ liệu nguồn.
- AC-07: Search theo tên hoạt động, không reload trang; khi không có kết quả hiển thị empty state.
- AC-08: Filter category cập nhật danh sách ngay; reset filter trả về danh sách ban đầu.
- AC-09: Sort đổi thứ tự sản phẩm đúng theo lựa chọn.

## 7.4 Product Detail
- AC-10: Gallery chuyển ảnh mượt, ảnh lớn cập nhật đúng theo thumbnail được chọn.
- AC-11: CTA “Liên hệ/ Nhận báo giá” điều hướng tới Contact và tự điền sản phẩm quan tâm (hoặc mở modal có sẵn thông tin sản phẩm).
- AC-12: Related products hiển thị tối đa 8 sản phẩm cùng danh mục và không chứa sản phẩm hiện tại.

## 7.5 Contact form
- AC-13: Các trường required không hợp lệ sẽ hiển thị lỗi inline và không submit.
- AC-14: Khi submit hợp lệ: nút chuyển sang trạng thái loading và disabled.
- AC-15: Submit thành công hiển thị thông báo thành công và reset form (trừ “Sản phẩm quan tâm” nếu readonly theo context).
- AC-16: Submit thất bại hiển thị thông báo lỗi và cho phép thử lại mà không mất dữ liệu người dùng đã nhập.

## 7.6 Responsive & accessibility
- AC-17: Giao diện không vỡ layout ở các breakpoint; grid sản phẩm chuyển cột hợp lý (1/2/3/4 cột).
- AC-18: Điều hướng bằng bàn phím: tab qua được các interactive elements; focus visible.
- AC-19: Tất cả ảnh sản phẩm có alt text; icon buttons có aria-label.

## 7.7 Performance basics
- AC-20: Ảnh trong danh sách sản phẩm dùng lazy-load; trang Products có skeleton trong lúc tải.
- AC-21: Lọc/tìm kiếm không gây giật lag rõ rệt với ~100 sản phẩm mock.

---

# 8) Recommended Frontend Scope (Gợi ý phạm vi MVP)
- MVP screens: Home, Products List, Product Detail, Contact, 404
- MVP components: Header (responsive), Footer, ProductCard, ProductGrid, Search+Filter bar, Gallery, ContactForm, Sticky CTA
- Data: mock JSON trước, tách service layer để dễ thay API sau (e.g. `productService.getAll()`, `getBySlug()`)

Nếu bạn cung cấp loại sản phẩm (VD: vật liệu xây dựng, đồ gia dụng, SaaS) và kênh liên hệ ưu tiên (hotline/Zalo/email), mình có thể chốt copy/CTA, cấu trúc category, và schema sản phẩm phù hợp hơn để dev React triển khai sát nhu cầu thực tế.