import React, { useState, useEffect } from 'react';
import { Terminal, ShieldAlert, Activity, FileText, CheckSquare, Server, Cpu, Database } from 'lucide-react';

const MagnitudePreviewBuilder = ({ moduleType }) => {
  const [step, setStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setStep((prev) => (prev < 5 ? prev + 1 : prev));
    }, 800);
    return () => clearInterval(interval);
  }, []);

  if (moduleType === 'tia') {
    const logs = [
      "> INITIALIZING MAGNITUDE AI...",
      "> EXTRACTING RAW THREAT DATA...",
      "> ISOLATING INDICATORS OF COMPROMISE (IOCs)...",
      "> PINGING SEPREP ENGINE FOR REPUTATION...",
      "> COMPILING ADVISORY...",
      "> GENERATION COMPLETE."
    ];

    return (
      <div className="flex-1 bg-black border-4 border-black p-6 flex flex-col font-mono text-neo-green h-full min-h-[400px]">
        <div className="flex items-center gap-2 mb-6 border-b-2 border-neo-green pb-2">
          <Terminal className="w-6 h-6" />
          <span className="font-black tracking-widest uppercase">Cyber-Terminal Active</span>
        </div>
        <div className="space-y-2 flex-1">
          {logs.map((log, index) => (
            <div 
              key={index} 
              className={`text-sm md:text-base font-bold transition-opacity duration-300 ${index <= step ? 'opacity-100' : 'opacity-0'}`}
            >
              {log}
            </div>
          ))}
          <div className="animate-pulse mt-2">_</div>
        </div>
      </div>
    );
  }

  if (moduleType === 'assessment') {
    const criteria = ["SECURITY PROTOCOLS", "COST EFFICIENCY", "USABILITY", "INTEGRATION", "COMPLIANCE"];
    
    return (
      <div className="flex-1 bg-white border-4 border-black p-6 h-full min-h-[400px] relative overflow-hidden">
        {/* Scanner line */}
        <div className="absolute left-0 right-0 h-2 bg-neo-accent animate-[scan_2s_ease-in-out_infinite] z-10 opacity-70"></div>
        
        <div className="flex items-center gap-2 mb-6 border-b-4 border-black pb-2">
          <CheckSquare className="w-6 h-6 text-neo-accent" />
          <span className="font-black text-xl tracking-widest uppercase">Interrogation Grid</span>
        </div>
        
        <div className="space-y-4">
          {criteria.map((item, index) => (
            <div key={index} className="flex items-center justify-between border-2 border-black p-3 bg-gray-50">
              <span className="font-bold">{item}</span>
              <div className="w-8 h-8 border-2 border-black flex items-center justify-center bg-white">
                {index < step && (
                  <span className={`text-2xl font-black ${index % 2 === 0 ? 'text-neo-green' : 'text-neo-accent'}`}>
                    {index % 2 === 0 ? '✓' : 'X'}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (moduleType === 'health') {
    const checks = [
      { name: "DATABASE LATENCY", icon: <Database className="w-5 h-5"/> },
      { name: "API ENDPOINTS", icon: <Server className="w-5 h-5"/> },
      { name: "CPU UTILIZATION", icon: <Cpu className="w-5 h-5"/> },
      { name: "MEMORY HEAP", icon: <Activity className="w-5 h-5"/> },
      { name: "NETWORK I/O", icon: <Activity className="w-5 h-5"/> }
    ];

    return (
      <div className="flex-1 bg-neo-blue border-4 border-black p-6 h-full min-h-[400px] text-white">
        <div className="flex items-center gap-2 mb-6 border-b-4 border-white pb-2">
          <Activity className="w-6 h-6 animate-pulse" />
          <span className="font-black text-xl tracking-widest uppercase">Diagnostic Radar</span>
        </div>
        
        <div className="space-y-4">
          {checks.map((check, index) => (
            <div key={index} className="flex items-center gap-4 bg-black p-3 border-2 border-black shadow-neo-sm">
              <div className="bg-white text-black p-2 rounded-sm">
                {check.icon}
              </div>
              <span className="font-bold flex-1">{check.name}</span>
              <div className={`px-3 py-1 border-2 border-white font-black text-sm ${index < step ? 'bg-neo-green text-black border-black' : 'bg-transparent text-white animate-pulse'}`}>
                {index < step ? '[ OK ]' : '[WAIT]'}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (moduleType === 'knowledge') {
    return (
      <div className="flex-1 bg-neo-yellow border-4 border-black p-6 h-full min-h-[400px] relative">
        <div className="flex items-center gap-2 mb-6 border-b-4 border-black pb-2">
          <FileText className="w-6 h-6" />
          <span className="font-black text-xl tracking-widest uppercase">Synthesizing Knowledge</span>
        </div>
        
        <div className="relative h-64">
          {/* Stacked Cards */}
          <div className="absolute top-0 left-0 right-8 bottom-8 bg-white border-4 border-black shadow-neo z-30 p-4 transition-transform duration-500 hover:-translate-y-2">
             <div className="w-1/2 h-4 bg-gray-200 mb-4 border-2 border-black"></div>
             {step > 1 && <div className="w-full h-2 bg-gray-300 mb-2"></div>}
             {step > 2 && <div className="w-5/6 h-2 bg-gray-300 mb-2"></div>}
             {step > 3 && <div className="w-4/6 h-2 bg-gray-300 mb-2"></div>}
             {step > 4 && <div className="w-full h-2 bg-gray-300 mb-2"></div>}
             <div className="absolute bottom-4 right-4 animate-spin">
               <Settings className="w-6 h-6"/>
             </div>
          </div>
          <div className="absolute top-4 left-4 right-4 bottom-4 bg-gray-100 border-4 border-black z-20"></div>
          <div className="absolute top-8 left-8 right-0 bottom-0 bg-gray-200 border-4 border-black z-10"></div>
        </div>
      </div>
    );
  }

  return null;
};

export default MagnitudePreviewBuilder;
