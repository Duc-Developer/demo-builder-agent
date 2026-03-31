# Slide 1;
slogan `Agent is slave. Human must be master`
image: triangle relationship between human vs agent. A closed circle, agents interact with agents, agents interact with humans. Agent must be confirmed from human

# Slide 1.1:
VD
Bài toán đưa ra cho nô lệ là "Hãy sản xuất lô xe tốt nhất để xuất khẩu"
Chinese Master: "tốt" nghĩa là Tao không cần chất lượng, xe chạy là được nhưng số lượng phải đưa lên hàng đầu
Japanese Master: "tốt" nghĩa là Tao không muốn bất cứ chiếc xe nào được gặp lỗi, chất lượng hơn số lượng.
`2 human khác nhau sẽ định nghĩa 1 kết quả khác nhau vì vậy agent cần phải có confirm của người dùng mỗi khi đưa ra 1 kết quả mới`

# Slide 2:
title: Communication vs knowledge là tối quan trọng. 
VD:
Ng VN, ng Nhật, ng Đức, ngừoi Ấn tất cả khi làm việc với nhau cần thông qua 1 ngôn ngữ chung (English)
Hệ thống chúng ta xây dựng trên cơ sở agent giao tiếp với human, agent giao tiếp với agent. Vì vâỵ cần thống nhất 1 định dạng giao tiếp. Best nhất hiện này là `.md`
- Tài liệu của BA phải là `.md`
- Test report của Tester phải là `.md`
- Dev phải có `.md` mô tả cho từng service của mình, dưới 1 mỗi service các func cũng phải có `.md` nhỏ để mô tả chức năng

Ưu điểm:
- Việc giao tiếp được cải thiện tối đa vì chung 1 định dạng dữ liệu > tiết kiệm token khi bundle file
- Knowledge được scale dễ dang sau này

# Slide 3:
Tất cả mọi hệ thống đều sẽ có ưu và nhược điểm nhất định:

Ưu điểm:
- crewai xây dựng bộ flow custom tùy theo mô hình và tính đặc thù của team, có thể bỏ qua hoặc tiếp tục với từng node trong flow
- Tích hợp được nhiều llm, kể cả các custom llm. Có thể phân chia llm phù hợp với từng agent. VD agent về code sẽ sử dụng claude, agent về Business sẽ sử dụng codex hoặc gemini,...
- Tích hợp được với mọi hệ thống của bên thứ3 mà team đang làm việc: github, gitlab, jira
- Token được kiểm soát hiệu quả
- Knowledge tốt hơn. Memory giữa human vs agent được tập trung tại 1 chỗ, giao tiếp hiệu quả qua `.md` file

Nhược điểm:
- Crewai xây dựng trên từ code, việc phát triển 1 flow sẽ rất tốn thời gian (tương đương với việc phát triển 1 project)
- flow được hash cứng, việc thay đổi flow sẽ cần code thêm. Nếu xây dựng platform để sắp xếp và tạo flow từ các agent sẵn có cũng sẽ tốn thời gian xây dựng hơn.