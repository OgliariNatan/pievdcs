import React from "react";
import ReactDOM from "react-dom";
import "./style.css";

function App() {
    return (
        <div>
            {/* Barra superior */}
            <nav className="top-nav">
                <ul className="menu">
                    <li>
                        <button>Fórum</button>
                        <ul className="submenu">
                            <li><button>Poder Judiciário</button></li>
                            <li><button>Ministério Público</button></li>
                            <li><button>Defensoria Pública</button></li>
                        </ul>
                    </li>
                    <li>
                        <button>Segurança Pública</button>
                        <ul className="submenu">
                            <li><button>Polícia Militar</button></li>
                            <li><button>Polícia Civil</button></li>
                            <li><button>Polícia Científica</button></li>
                            <li><button>Polícia Penal</button></li>
                        </ul>
                    </li>
                    <li>
                        <button>Município</button>
                        <ul className="submenu">
                            <li><button>Assistência Social</button></li>
                            <li><button>Conselho Tutelar</button></li>
                        </ul>
                    </li>
                </ul>
            </nav>

            {/* Barra lateral */}
            <aside className="sidebar">
                <button>Atendimento Realizado</button>
                <button>Encaminhamentos</button>
                <button>Notificações</button>
            </aside>

            {/* Conteúdo principal */}
            <div id="root-content">
                <h1>Bem-vindo ao Sistema de Segurança Pública!</h1>
            </div>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById("root"));