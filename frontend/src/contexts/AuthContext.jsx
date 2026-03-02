import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const AuthContext = createContext();

// Em produção (sem VITE_API_URL fixada), usa caminho relativo '' para apontar para o próprio adsai.com.br
const API_URL = import.meta.env.VITE_API_URL || '';

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        // Tenta carregar usuário persistido
        const checkAuth = async () => {
            const token = localStorage.getItem('hana_token');
            if (token) {
                try {
                    // Neste template não existe rota /me, mas podemos abstrair ou bater nela para checar validade.
                    // Como fizemos no token_type return user, podemos guardar tudo no LocalStorage
                    const storedUser = localStorage.getItem('hana_user');
                    if (storedUser) {
                        setUser(JSON.parse(storedUser));
                    } else {
                        // Se tiver token mas não tiver user local, limpa tudo.
                        logout();
                    }
                } catch (error) {
                    logout();
                }
            }
            setLoading(false);
        };

        checkAuth();
    }, []);

    const loginStep1 = async (email, password) => {
        try {
            const response = await axios.post(`${API_URL}/api/v1/auth/login`, { email, password });
            return response.data; // Retorna status: 'requires_2fa' e mensagem
        } catch (error) {
            throw error.response?.data?.detail || "Erro ao tentar realizar login. Verifique suas credenciais.";
        }
    };

    const loginStep2 = async (email, code) => {
        try {
            const response = await axios.post(`${API_URL}/api/v1/auth/verify-2fa`, { email, code });
            const { access_token, user } = response.data;

            localStorage.setItem('hana_token', access_token);
            localStorage.setItem('hana_user', JSON.stringify(user));

            setUser(user);
            navigate('/dashboard/radar'); // Redireciona à página inicial
            return true;
        } catch (error) {
            throw error.response?.data?.detail || "Código inválido.";
        }
    };

    const logout = () => {
        localStorage.removeItem('hana_token');
        localStorage.removeItem('hana_user');
        setUser(null);
        navigate('/login');
    };

    return (
        <AuthContext.Provider value={{ user, loading, loginStep1, loginStep2, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export const useAuth = () => useContext(AuthContext);
