"use client";
import {Monitor,Moon,Sun} from "lucide-react";
import {useTheme} from "./theme-provider";
export function ThemeSwitcher(){const {theme,setTheme}=useTheme();return <div className="theme-switch"><button aria-pressed={theme==="light"} onClick={()=>setTheme("light")} title="Light"><Sun size={16}/></button><button aria-pressed={theme==="dark"} onClick={()=>setTheme("dark")} title="Dark"><Moon size={16}/></button><button aria-pressed={theme==="system"} onClick={()=>setTheme("system")} title="System"><Monitor size={16}/></button></div>}
