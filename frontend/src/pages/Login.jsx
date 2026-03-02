import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Shield, Lock, ChevronRight, User } from 'lucide-react';

export default function Login() {
    const { loginStep1, loginStep2 } = useAuth();
    const [step, setStep] = useState(1);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [code, setCode] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState(''); // Mensagem do envio 2FA

    const handleStep1 = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const res = await loginStep1(email, password);
            if (res.status === 'requires_2fa') {
                setMessage(res.message);
                setStep(2);

                // Em dev_mode o backend devolve a senha para debug
                if (res._dev_code) {
                    console.log("DEV 2FA CODE:", res._dev_code);
                }
            }
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    const handleStep2 = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            await loginStep2(email, code);
            // O redirect já acontece dentro do AuthContext
        } catch (err) {
            setError(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-[#0d0905] text-[#ead899] font-sans relative overflow-hidden">

            {/* Background Decorativo */}
            <div className="absolute top-[-100px] left-[-100px] w-[500px] h-[500px] bg-[#d5aa53] rounded-full filter blur-[200px] opacity-10"></div>
            <div className="absolute bottom-[-100px] right-[-100px] w-[500px] h-[500px] bg-[#d5aa53] rounded-full filter blur-[200px] opacity-10"></div>

            <div className="relative w-full max-w-md bg-[#130f0c] rounded-2xl border border-[#d5aa53]/20 shadow-[0_0_50px_rgba(213,170,83,0.05)] p-10 z-10 transition-transform duration-500 ease-out hover:-translate-y-1">

                <div className="text-center mb-10">
                    <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-[#1c1813] border border-[#d5aa53]/30 text-[#d5aa53] mb-4 shadow-[0_0_20px_rgba(213,170,83,0.1)]">
                        <Shield size={32} />
                    </div>
                    <h1 className="text-3xl font-extrabold tracking-wider bg-clip-text text-transparent bg-gradient-to-r from-[#ead899] via-[#d5aa53] to-[#ead899]">
                        HANA INTEL
                    </h1>
                    <p className="text-[#a49174] text-sm tracking-widest uppercase mt-2 font-medium">Enterprise Core</p>
                </div>

                {error && (
                    <div className="mb-6 p-4 rounded-lg bg-red-900/20 border border-red-500/30 text-red-200 text-sm text-center">
                        {error}
                    </div>
                )}

                {step === 1 ? (
                    <form onSubmit={handleStep1} className="space-y-6">
                        <div className="space-y-2">
                            <label className="text-xs uppercase tracking-widest text-[#a49174] font-semibold">Credencial de Acesso</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#d5aa53]">
                                    <User size={18} />
                                </div>
                                <input
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-[#1c1813] border border-[#d5aa53]/20 rounded-xl text-white placeholder-[#a49174] focus:outline-none focus:border-[#d5aa53] focus:ring-1 focus:ring-[#d5aa53] transition-colors"
                                    placeholder="Seu E-mail C-Level"
                                    required
                                />
                            </div>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs uppercase tracking-widest text-[#a49174] font-semibold">Assinatura Digital</label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#d5aa53]">
                                    <Lock size={18} />
                                </div>
                                <input
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full pl-10 pr-4 py-3 bg-[#1c1813] border border-[#d5aa53]/20 rounded-xl text-white placeholder-[#a49174] focus:outline-none focus:border-[#d5aa53] focus:ring-1 focus:ring-[#d5aa53] transition-colors"
                                    placeholder="• • • • • • • •"
                                    required
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-4 mt-4 bg-gradient-to-r from-[#d5aa53] to-[#c79836] hover:from-[#e3b860] hover:to-[#d5aa53] text-[#130f0c] font-bold rounded-xl shadow-lg transition-all duration-300 transform hover:scale-[1.02] flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50 disabled:hover:scale-100"
                        >
                            <span>{loading ? 'Autenticando...' : 'Autenticar'}</span>
                            {!loading && <ChevronRight size={18} />}
                        </button>
                    </form>
                ) : (
                    <form onSubmit={handleStep2} className="space-y-6 animate-fade-in-up">
                        <div className="text-center mb-6">
                            <p className="text-sm text-[#a49174] leading-relaxed">{message}</p>
                        </div>

                        <div className="space-y-2">
                            <label className="text-xs uppercase tracking-widest text-[#a49174] font-semibold text-center block">Código 2FA (WhatsApp)</label>
                            <input
                                type="text"
                                maxLength="6"
                                value={code}
                                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))} // Apenas Numeros
                                className="w-full py-4 text-center text-3xl tracking-[1em] bg-[#1c1813] border border-[#d5aa53]/50 rounded-xl text-[#ead899] font-mono focus:outline-none focus:border-[#d5aa53] focus:shadow-[0_0_15px_rgba(213,170,83,0.3)] transition-all transition-shadow"
                                placeholder="000000"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading || code.length < 6}
                            className="w-full py-4 mt-4 bg-gradient-to-r from-[#d5aa53] to-[#c79836] hover:from-[#e3b860] hover:to-[#d5aa53] text-[#130f0c] font-bold rounded-xl shadow-lg transition-all duration-300 transform hover:scale-[1.02] flex items-center justify-center space-x-2 cursor-pointer disabled:opacity-50 disabled:hover:scale-100"
                        >
                            <span>{loading ? 'Verificando...' : 'Autorizar Base'}</span>
                            {!loading && <ChevronRight size={18} />}
                        </button>

                        <div className="text-center pt-4">
                            <button
                                type="button"
                                onClick={() => { setStep(1); setCode(''); }}
                                className="text-xs text-[#d5aa53] hover:text-[#ead899] underline underline-offset-4 opacity-70 hover:opacity-100 transition-opacity cursor-pointer"
                            >
                                Voltar e usar credenciais alternativas
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}
