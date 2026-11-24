"use client";
import {createContext,useContext,useEffect,useMemo,useState} from "react";
type Theme="light"|"dark"|"system";
const C=createContext<{theme:Theme;setTheme:(v:Theme)=>void}>({theme:"system",setTheme:()=>{}});
export const useTheme=()=>useContext(C);
export function ThemeProvider({children}:{children:React.ReactNode}){
 const [theme,setTheme]=useState<Theme>("system");
 useEffect(()=>{const saved=localStorage.getItem("verilex-theme") as Theme|null;if(saved)setTheme(saved)},[]);
 useEffect(()=>{const apply=()=>{document.documentElement.dataset.theme=theme==="dark"||(theme==="system"&&matchMedia("(prefers-color-scheme: dark)").matches)?"dark":"light"};apply();localStorage.setItem("verilex-theme",theme);const m=matchMedia("(prefers-color-scheme: dark)");m.addEventListener("change",apply);return()=>m.removeEventListener("change",apply)},[theme]);
 const value=useMemo(()=>({theme,setTheme}),[theme]);return <C.Provider value={value}>{children}</C.Provider>
}
