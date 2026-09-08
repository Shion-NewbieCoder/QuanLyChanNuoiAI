const scaffoldBoundaries = [
  {
    label: "Nguồn dữ liệu",
    title: "Django là hệ thống chính",
    detail: "React chỉ tiêu thụ dữ liệu qua API đã được phân quyền.",
  },
  {
    label: "Phiên đăng nhập",
    title: "Xác thực cùng origin",
    detail: "Không tạo JWT, token storage hay một luồng đăng nhập thứ hai.",
  },
  {
    label: "Nghiệp vụ & AI",
    title: "Backend giữ quyền quyết định",
    detail: "Phân quyền, thống kê và kết quả AI vẫn do các boundary hiện có xử lý.",
  },
];


function App() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <a className="brand" href="/dashboard/" aria-label="Mở Django Dashboard">
          <span className="brand-mark" aria-hidden="true">N8</span>
          <span>
            <strong>Nông trại AI</strong>
            <small>Quản lý chăn nuôi gia súc</small>
          </span>
        </a>
        <nav aria-label="Điều hướng scaffold">
          <a href="#readiness">Trạng thái</a>
          <a href="#boundaries">Kiến trúc</a>
          <a className="dashboard-link" href="/dashboard/">Django Dashboard</a>
        </nav>
      </header>

      <main>
        <section className="hero" id="readiness">
          <div className="hero-copy">
            <p className="eyebrow">Vite + React foundation</p>
            <h1>Sẵn sàng cho tích hợp giao diện trong tương lai.</h1>
            <p className="hero-description">
              App shell này xác lập ranh giới frontend rõ ràng mà không thay thế
              dashboard Django, không sao chép business logic và không chứa dữ liệu demo.
            </p>
            <div className="hero-actions">
              <a className="primary-action" href="/dashboard/">Mở dashboard hiện tại</a>
              <span className="status" role="status">
                <span aria-hidden="true" /> Scaffold sẵn sàng
              </span>
            </div>
          </div>
          <aside className="readiness-panel" aria-label="Phạm vi TSK-026">
            <p className="panel-kicker">TSK-026</p>
            <h2>Scaffold only</h2>
            <ul>
              <li>React application shell</li>
              <li>Same-origin API boundary</li>
              <li>Responsive, accessible baseline</li>
            </ul>
            <p className="panel-note">Không CRUD UI · Không router · Không auth mới</p>
          </aside>
        </section>

        <section className="boundaries" id="boundaries" aria-labelledby="boundaries-title">
          <div className="section-heading">
            <p className="eyebrow">Ranh giới tích hợp</p>
            <h2 id="boundaries-title">Frontend nhẹ, backend quyết định.</h2>
          </div>
          <div className="boundary-grid">
            {scaffoldBoundaries.map((item, index) => (
              <article className="boundary-card" key={item.label}>
                <span className="card-number">0{index + 1}</span>
                <p>{item.label}</p>
                <h3>{item.title}</h3>
                <span>{item.detail}</span>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer>
        <span>Nhóm 08</span>
        <span>Vite / React scaffold</span>
      </footer>
    </div>
  );
}

export default App;
