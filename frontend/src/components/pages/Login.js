import { useRef, useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthContext from "../../context/AuthProvider";
import './login.css';

import axios from '../../api/axios';
const LOGIN_URL = 'http://localhost:8000/api/auth/login';

const Login = () => {
    const { setAuth } = useContext(AuthContext);
    const userRef = useRef();
    const errRef = useRef();
    const navigate = useNavigate();

    const [user, setUser] = useState('');
    const [pwd, setPwd] = useState('');
    const [dtp, setDtp] = useState(''); 
    const [errMsg, setErrMsg] = useState('');
    const [success, setSuccess] = useState(false);

    useEffect(() => {
        userRef.current.focus();
    }, [])

    useEffect(() => {
        setErrMsg('');
    }, [user, pwd])

    const handleSubmit = async (e) => {
        e.preventDefault();
    
        try {
            const formData = new FormData();
            formData.append('username', user);
            formData.append('password', pwd);
    
            const response = await axios.post(LOGIN_URL, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                withCredentials: false
            });

            console.log(JSON.stringify(response?.data.access_token));
    
            const accessToken = response.data.access_token;

            localStorage.setItem('REACT_APP_DTP_TOKEN', dtp);
            localStorage.setItem('REACT_APP_OAUTH2_TOKEN', accessToken);

            setAuth({ user, pwd, accessToken });
            setUser('');
            setPwd('');
            setSuccess(true);

            navigate('/home');
        } catch (err) {
            if (!err?.response) {
                setErrMsg('No Server Response');
            } else if (err.response?.status === 400) {
                setErrMsg('Missing Username or Password');
            } else if (err.response?.status === 401) {
                setErrMsg('Unauthorized');
            } else {
                setErrMsg('Login Failed');
            }
            console.log(err);
            errRef.current.focus();
        }
    }

    return (
        <>
            {success ? (
                <section>
                    <h1>You are logged in!</h1>
                    <br />
                    <p>
                        <a href="#">Go to Home</a>
                    </p>
                </section>
            ) : (
                <section>
                    <div className='sec_in'>
                    <p ref={errRef} className={errMsg ? "errmsg" : "offscreen"} aria-live="assertive">{errMsg}</p>
                    
                    <h1 className='header_name'>Sign In</h1>
                    <form onSubmit={handleSubmit}>
                        <label htmlFor="username">Username</label>
                        <input
                            type="text"
                            id="username"
                            ref={userRef}
                            autoComplete="off"
                            onChange={(e) => setUser(e.target.value)}
                            value={user}
                            required
                        />

                        <label htmlFor="password">DTP Code</label>
                        <input
                            type="text"
                            id="dtp_code"
                            ref={userRef}
                            autoComplete="off"
                            onChange={(e) => setDtp(e.target.value)}
                            value={dtp}
                            required
                        />

                        <label htmlFor="username">Password</label>
                        <input
                            type="password"
                            id="password"
                            onChange={(e) => setPwd(e.target.value)}
                            value={pwd}
                            required
                        />
                        <button>Login</button>
                    </form>
                    </div>
                    
                </section>
            )}
        </>
    )
}

export default Login
