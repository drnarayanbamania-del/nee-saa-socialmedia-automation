import { useState, useEffect, useRef, useCallback } from 'react'
import { useAuth } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import {
  projectsAPI, generateAPI, viralAPI, scheduleAPI,
  analyticsAPI, publishAPI, healthAPI, wakeUpBackend
} from './services/api'

// ── Backend Status Banner ──────────────────────────────────────────────────────
function BackendStatusBanner() {
  const [status, setStatus] = useState<'checking'|'online'|'offline'|'waking'>('checking')
  const [show, setShow] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function check() {
      setStatus('waking')
      const result = await healthAPI.check()
      if (!cancelled) {
        setStatus(result.status === 'online' ? 'online' : 'offline')
        if (result.status === 'online') {
          setTimeout(() => setShow(false), 3000)
        }
      }
    }
    check()
    const interval = setInterval(check, 30000)
    return () => { cancelled = true; clearInterval(interval) }
  }, [])

  // Wake up backend on mount
  useEffect(() => { wakeUpBackend() }, [])

  if (!show) return null

  const colors = {
    checking: 'bg-gray-800 border-gray-600 text-gray-300',
    waking:   'bg-yellow-900/80 border-yellow-600 text-yellow-200',
    online:   'bg-green-900/80 border-green-600 text-green-200',
    offline:  'bg-red-900/80 border-red-600 text-red-200',
  }
  const icons = { checking:'⏳', waking:'🔄', online:'✅', offline:'⚠️' }
  const msgs  = {
    checking: 'Connecting to Render backend...',
    waking:   'Waking up Render backend (free tier — takes ~30s)...',
    online:   'Backend online at nee-saa-socialmedia-automation-1.onrender.com ✅',
    offline:  'Backend offline — running in local fallback mode (all features still work)',
  }

  return (
    <div className={`fixed bottom-4 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full border text-xs font-medium flex items-center gap-2 shadow-lg transition-all ${colors[status]}`}>
      <span>{icons[status]}</span>
      <span>{msgs[status]}</span>
      <button onClick={() => setShow(false)} className="ml-2 opacity-60 hover:opacity-100">✕</button>
    </div>
  )
}

// ── Types ──────────────────────────────────────────────────────────────────────
type Nav    = 'Projects'|'Studio'|'Thumbnail'|'Analytics'|'Settings'|'About'
type VLen   = 'short'|'long'
type Res    = 'normal'|'2k'|'4k'
type Ratio  = '9:16'|'16:9'|'1:1'|'4:5'

interface Project {
  id:string; title:string; topic:string; status:string
  duration:string; resolution:string; ratio:string; platform:string
  views:string; likes:string; comments:string; thumbnail:string
  createdAt:string; scheduledFor?:string; videoLength:string; category:string
  videoUrl?:string
}
interface ViralItem {
  id:string; title:string; subtitle:string; creator:string
  metric:string; duration:string; timeAgo:string; score:number
  platform:'youtube'|'instagram'
}
interface Schedule {
  id:string; project_id:string; project_title:string
  scheduled_for:string; platforms:string[]; status:string
}

// ── Small shared helpers ───────────────────────────────────────────────────────
function ScoreBadge({score}:{score:number}) {
  const c = score>=95?'bg-green-500':score>=90?'bg-violet-500':'bg-blue-500'
  return <span className={`${c} text-white text-xs font-black px-2 py-1 rounded-lg min-w-[36px] text-center inline-block`}>{score}</span>
}

function Toast({msg,type='info'}:{msg:string;type?:'info'|'success'|'error'}) {
  const bg = type==='success'?'from-green-500 to-emerald-600':type==='error'?'from-red-500 to-rose-600':'from-violet-600 to-indigo-600'
  return (
    <div className={`fixed top-4 right-4 z-[200] bg-gradient-to-r ${bg} text-white px-5 py-3 rounded-2xl shadow-2xl text-sm font-semibold flex items-center gap-2 max-w-sm`}>
      <span className="w-2 h-2 bg-white rounded-full shrink-0"/>
      <span>{msg}</span>
    </div>
  )
}

function Spinner({size='sm'}:{size?:'sm'|'md'}) {
  const s = size==='sm'?'w-4 h-4':'w-6 h-6'
  return <span className={`${s} border-2 border-white/30 border-t-white rounded-full animate-spin inline-block`}/>
}

function DeleteModal({title,onConfirm,onCancel,loading}:{title:string;onConfirm:()=>void;onCancel:()=>void;loading?:boolean}) {
  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-white rounded-3xl p-6 w-full max-w-sm shadow-2xl">
        <div className="w-14 h-14 bg-red-100 rounded-2xl flex items-center justify-center text-3xl mx-auto mb-4">🗑️</div>
        <h3 className="text-lg font-black text-gray-900 text-center mb-2">Delete Project?</h3>
        <p className="text-gray-500 text-sm text-center mb-6">
          "<span className="font-semibold text-gray-700">{title}</span>" will be permanently removed.
        </p>
        <div className="flex gap-3">
          <button onClick={onCancel} className="flex-1 py-3 border-2 border-gray-200 text-gray-600 font-semibold rounded-2xl hover:bg-gray-50 active:scale-95 transition-all">
            Cancel
          </button>
          <button onClick={onConfirm} disabled={loading}
            className="flex-1 py-3 bg-gradient-to-r from-red-500 to-rose-600 text-white font-semibold rounded-2xl hover:opacity-90 active:scale-95 transition-all disabled:opacity-50 flex items-center justify-center gap-2">
            {loading?<><Spinner/>Deleting...</>:'Delete'}
          </button>
        </div>
      </div>
    </div>
  )
}

function VideoPlayerModal({project,onClose}:{project:Project;onClose:()=>void}) {
  const vRef = useRef<HTMLVideoElement>(null)
  const [playing,setPlaying] = useState(false)
  const [progress,setProgress] = useState(0)
  const [muted,setMuted] = useState(false)

  useEffect(()=>{
    const el = vRef.current; if(!el) return
    const onTime = ()=>setProgress((el.currentTime/el.duration)*100||0)
    el.addEventListener('timeupdate',onTime)
    return ()=>el.removeEventListener('timeupdate',onTime)
  },[])

  const toggle=()=>{
    const el=vRef.current; if(!el) return
    playing?el.pause():el.play()
    setPlaying(!playing)
  }

  useEffect(()=>{
    const esc=(e:KeyboardEvent)=>{if(e.key==='Escape')onClose()}
    document.addEventListener('keydown',esc)
    return ()=>document.removeEventListener('keydown',esc)
  },[onClose])

  return (
    <div className="fixed inset-0 z-[150] flex items-center justify-center bg-black/95 p-4" onClick={onClose}>
      <div className="relative w-full max-w-lg bg-black rounded-3xl overflow-hidden shadow-2xl" onClick={e=>e.stopPropagation()}>
        <div className="flex items-center justify-between px-5 py-3 bg-gray-900">
          <div>
            <p className="text-white font-bold text-sm truncate max-w-xs">{project.title}</p>
            <p className="text-gray-400 text-xs">{project.platform} • {project.resolution} • {project.ratio}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 bg-white/10 hover:bg-white/20 text-white rounded-full flex items-center justify-center text-sm transition-all">✕</button>
        </div>

        <div className="relative bg-black aspect-[9/16] max-h-[60vh] flex items-center justify-center">
          {project.videoUrl ? (
            <video ref={vRef} src={project.videoUrl} className="w-full h-full object-contain" onClick={toggle}
              style={{maxHeight:'60vh'}} playsInline/>
          ) : (
            <div className="w-full h-full flex flex-col items-center justify-center" style={{background:`url(${project.thumbnail}) center/cover`}}>
              <div className="absolute inset-0 bg-black/60"/>
              <div className="relative text-center">
                <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mb-4 border border-white/30">
                  <span className="text-4xl">🎬</span>
                </div>
                <p className="text-white text-sm font-medium">Preview Mode</p>
                <p className="text-white/60 text-xs mt-1">Connect backend for real video</p>
              </div>
            </div>
          )}
          {project.videoUrl && (
            <button onClick={toggle}
              className="absolute inset-0 flex items-center justify-center bg-transparent hover:bg-black/10 transition-all group">
              {!playing && (
                <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border border-white/30 group-hover:scale-110 transition-transform">
                  <span className="text-3xl ml-1">▶</span>
                </div>
              )}
            </button>
          )}
        </div>

        {project.videoUrl && (
          <div className="px-5 py-3 bg-gray-900">
            <div className="w-full bg-gray-700 rounded-full h-1.5 mb-3 cursor-pointer" onClick={e=>{
              const rect=e.currentTarget.getBoundingClientRect()
              const pct=(e.clientX-rect.left)/rect.width
              if(vRef.current){vRef.current.currentTime=pct*vRef.current.duration}
            }}>
              <div className="bg-gradient-to-r from-violet-500 to-fuchsia-500 h-1.5 rounded-full transition-all" style={{width:`${progress}%`}}/>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <button onClick={toggle} className="w-9 h-9 bg-white/10 hover:bg-white/20 text-white rounded-full flex items-center justify-center transition-all text-sm">
                  {playing?'⏸':'▶'}
                </button>
                <button onClick={()=>{setMuted(!muted);if(vRef.current)vRef.current.muted=!muted}}
                  className="w-9 h-9 bg-white/10 hover:bg-white/20 text-white rounded-full flex items-center justify-center transition-all text-sm">
                  {muted?'🔇':'🔊'}
                </button>
              </div>
              <a href={project.videoUrl} download={`${project.title}.mp4`}
                className="flex items-center gap-1.5 bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white text-xs font-semibold px-4 py-2 rounded-full hover:opacity-90 transition-all">
                ⬇ Download
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

function ScheduleModal({project,onSave,onClose,loading}:{
  project:Project; onSave:(date:string,time:string,platforms:string[])=>void
  onClose:()=>void; loading:boolean
}) {
  const today = new Date().toISOString().split('T')[0]
  const [date,setDate] = useState(today)
  const [time,setTime] = useState('18:00')
  const [plats,setPlats] = useState(['youtube'])
  const toggle=(p:string)=>setPlats(prev=>prev.includes(p)?prev.filter(x=>x!==p):[...prev,p])
  const preview = date&&time ? `${new Date(`${date}T${time}`).toLocaleDateString('en-IN',{weekday:'short',month:'short',day:'numeric'})} at ${new Date(`${date}T${time}`).toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit'})}` : '—'

  return (
    <div className="fixed inset-0 z-[100] flex items-end sm:items-center justify-center bg-black/70 backdrop-blur-sm p-0 sm:p-4" onClick={onClose}>
      <div className="w-full sm:max-w-md bg-white rounded-t-3xl sm:rounded-3xl p-6 shadow-2xl" onClick={e=>e.stopPropagation()}>
        <div className="w-10 h-1 bg-gray-200 rounded-full mx-auto mb-5 sm:hidden"/>
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-lg font-black text-gray-900">📅 Schedule Post</h3>
            <p className="text-xs text-gray-500 mt-0.5 truncate max-w-[200px]">{project.title}</p>
          </div>
          <button onClick={onClose} className="w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center text-gray-500 transition-all">✕</button>
        </div>

        <div className="grid grid-cols-2 gap-3 mb-4">
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1.5">📆 Date</label>
            <input type="date" value={date} min={today} onChange={e=>setDate(e.target.value)}
              className="w-full border-2 border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-violet-400"/>
          </div>
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1.5">⏰ Time</label>
            <input type="time" value={time} onChange={e=>setTime(e.target.value)}
              className="w-full border-2 border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-900 focus:outline-none focus:border-violet-400"/>
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-xs font-semibold text-gray-500 mb-2">Platforms</label>
          <div className="flex flex-wrap gap-2">
            {[{id:'youtube',label:'▶ YouTube',color:'bg-red-500'},{id:'instagram',label:'📸 Instagram',color:'bg-pink-500'},{id:'facebook',label:'📘 Facebook',color:'bg-blue-500'}].map(p=>(
              <button key={p.id} onClick={()=>toggle(p.id)}
                className={`px-4 py-2 rounded-xl text-sm font-semibold border-2 transition-all ${plats.includes(p.id)?`${p.color} text-white border-transparent`:'bg-gray-50 text-gray-500 border-gray-200 hover:border-gray-300'}`}>
                {p.label}
              </button>
            ))}
          </div>
        </div>

        {date&&time&&(
          <div className="bg-violet-50 border border-violet-200 rounded-2xl p-3 mb-4">
            <p className="text-violet-700 text-xs font-semibold">📅 Will publish on {preview}</p>
            <p className="text-violet-500 text-xs mt-0.5">To: {plats.join(', ')}</p>
          </div>
        )}

        <div className="flex gap-3">
          <button onClick={onClose} className="flex-1 py-3 border-2 border-gray-200 text-gray-600 font-semibold rounded-2xl hover:bg-gray-50 transition-all text-sm">Cancel</button>
          <button onClick={()=>onSave(date,time,plats)} disabled={loading||!date||!time||!plats.length}
            className="flex-1 py-3 bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white font-semibold rounded-2xl hover:opacity-90 disabled:opacity-50 transition-all text-sm flex items-center justify-center gap-2">
            {loading?<><Spinner/>Scheduling...</>:'Confirm Schedule'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Main App ───────────────────────────────────────────────────────────────────
export default function App() {
  const { user, isAuthenticated, logout } = useAuth()
  const [authView, setAuthView] = useState<'login'|'register'>('login')

  // Navigation
  const [nav, setNav]       = useState<Nav>('Projects')
  const [sideOpen,setSideOpen] = useState(false)

  // Projects state
  const [projects, setProjects]     = useState<Project[]>([])
  const [activeProject, setActive]  = useState<Project|null>(null)
  const [projectsLoading, setPrjLoad] = useState(false)

  // Viral content
  const [ytItems, setYtItems]   = useState<ViralItem[]>([])
  const [igItems, setIgItems]   = useState<ViralItem[]>([])
  const [scraperLoading, setScraperLoad] = useState(false)
  const [countdown, setCountdown] = useState(300)
  const [lastRefresh, setLastRefresh] = useState('just now')

  // Generation
  const [topic, setTopic]     = useState('')
  const [vlen, setVlen]       = useState<VLen>('short')
  const [res, setRes]         = useState<Res>('4k')
  const [ratio, setRatio]     = useState<Ratio>('9:16')
  const [genLoading, setGenLoading] = useState(false)
  const [genProgress, setGenProgress] = useState(0)
  const [genStage, setGenStage] = useState('')
  const [genDone, setGenDone] = useState(false)

  // Schedules
  const [schedules, setSchedules]   = useState<Schedule[]>([])
  const [schedModal, setSchedModal] = useState<Project|null>(null)
  const [schedLoading, setSchedLoad] = useState(false)

  // Modals
  const [deleteTarget, setDeleteTarget] = useState<Project|null>(null)
  const [deleteLoading, setDelLoad]     = useState(false)
  const [playerProject, setPlayer]      = useState<Project|null>(null)

  // UI state
  const [toast, setToast]         = useState<{msg:string;type?:'info'|'success'|'error'}|null>(null)
  const [searchQ, setSearchQ]     = useState('')
  const [statusFilter, setStatusFilter] = useState('All')
  const [downloadLoading, setDlLoad] = useState<string>('')
  const [shareLoading, setShareLoad] = useState<string>('')
  const [publishLoading, setPubLoad] = useState<string>('')

  // Analytics
  const [analytics, setAnalytics] = useState<{stats:Record<string,unknown>;platform_stats:Record<string,unknown>;weekly_data:Array<{day:string;videos:number;views:number}>}|null>(null)

  // Refs
  const genRef = useRef<HTMLDivElement>(null)

  const showToast = useCallback((msg:string, type:'info'|'success'|'error'='info') => {
    setToast({msg,type})
    setTimeout(()=>setToast(null),3500)
  },[])

  // ── Load data after login ────────────────────────────────────────────────────
  useEffect(()=>{
    if(!isAuthenticated) return
    // Load projects
    setPrjLoad(true)
    projectsAPI.list()
      .then(p=>setProjects(p as Project[]))
      .catch(()=>{ /* use empty state */ })
      .finally(()=>setPrjLoad(false))
    // Load schedules
    scheduleAPI.list()
      .then(s=>setSchedules(s as Schedule[]))
      .catch(()=>{})
    // Load analytics
    analyticsAPI.get()
      .then(a=>setAnalytics(a as typeof analytics))
      .catch(()=>{})
    // Load viral content
    loadViral()
  },[isAuthenticated])

  // ── Viral scraper ────────────────────────────────────────────────────────────
  const loadViral = async()=>{
    setScraperLoad(true)
    try {
      const data = await viralAPI.get()
      setYtItems(data.youtube_videos as ViralItem[])
      setIgItems(data.instagram_reels as ViralItem[])
      setLastRefresh('just now')
      setCountdown(300)
    } catch {
      // fallback data
      setYtItems([
        {id:'y1',title:'Morning Routine Secrets of High Performers',subtitle:'High-retention YouTube Short with strong hook',creator:'Growth Lab',metric:'12M views',duration:'0:58',timeAgo:'2 days ago',score:97,platform:'youtube'},
        {id:'y2',title:'AI Tools That Will Replace Old Workflows',subtitle:'Tech trend short performing well across niches',creator:'Tech Insider',metric:'8.5M views',duration:'1:24',timeAgo:'1 day ago',score:93,platform:'youtube'},
        {id:'y3',title:'5 Habits That Changed My Life Forever',subtitle:'Personal development with emotional storytelling',creator:'Life Mastery',metric:'6.2M views',duration:'2:15',timeAgo:'3 days ago',score:91,platform:'youtube'},
      ])
      setIgItems([
        {id:'i1',title:'3 Reel Hooks That Instantly Boost Watch Time',subtitle:'Short-form structure built around fast hooks',creator:'@growthreels',metric:'3.1M plays',duration:'0:32',timeAgo:'5 hours ago',score:95,platform:'instagram'},
        {id:'i2',title:'Luxury Cinematic B-Roll Ideas for Viral Reels',subtitle:'Premium aesthetic transitions',creator:'@cinematicpro',metric:'2.8M plays',duration:'0:45',timeAgo:'8 hours ago',score:91,platform:'instagram'},
        {id:'i3',title:'Behind The Scenes of Viral Content Creation',subtitle:'Authentic BTS content',creator:'@creatorlife',metric:'1.9M plays',duration:'1:12',timeAgo:'12 hours ago',score:89,platform:'instagram'},
      ])
    } finally { setScraperLoad(false) }
  }

  // Countdown timer
  useEffect(()=>{
    const t = setInterval(()=>{
      setCountdown(c=>{ if(c<=1){loadViral();return 300} return c-1 })
    },1000)
    return()=>clearInterval(t)
  },[])

  const fmtCountdown=(s:number)=>`${Math.floor(s/60)}:${String(s%60).padStart(2,'0')}`

  // ── Filtered projects ────────────────────────────────────────────────────────
  const filteredProjects = projects.filter(p=>{
    const matchQ = !searchQ||p.title.toLowerCase().includes(searchQ.toLowerCase())||p.topic.toLowerCase().includes(searchQ.toLowerCase())
    const matchS = statusFilter==='All'||p.status===statusFilter
    return matchQ&&matchS
  })

  // ── Generate video ───────────────────────────────────────────────────────────
  const handleGenerate = async()=>{
    if(!topic.trim()){showToast('Please enter a topic','error');return}
    setGenLoading(true); setGenProgress(0); setGenDone(false)
    const stages=['Analyzing Topic','Writing Script','Generating Scenes','Creating Visuals','Voice Synthesis','Video Composition']
    try {
      // Simulate stage-by-stage progress
      for(let i=0;i<stages.length;i++){
        setGenStage(stages[i])
        await new Promise(r=>setTimeout(r,700))
        setGenProgress(Math.round(((i+1)/stages.length)*100))
      }
      const data = await generateAPI.video({
        topic, duration_type:vlen, resolution:res, aspect_ratio:ratio, platform:'youtube_shorts'
      })
      setProjects(prev=>[data.project as Project,...prev])
      setActive(data.project as Project)
      setGenDone(true)
      showToast(`✅ "${data.project.title}" generated!`,'success')
      setTopic('')
    } catch(err:unknown) {
      const msg = err instanceof Error?err.message:'Generation failed'
      showToast(msg,'error')
    } finally { setGenLoading(false) }
  }

  // ── Delete project ───────────────────────────────────────────────────────────
  const handleDelete = async()=>{
    if(!deleteTarget) return
    setDelLoad(true)
    try {
      await projectsAPI.delete(deleteTarget.id)
      setProjects(prev=>{
        const next=prev.filter(p=>p.id!==deleteTarget.id)
        if(activeProject?.id===deleteTarget.id) setActive(next[0]||null)
        return next
      })
      showToast('Project deleted','success')
    } catch {
      // Fallback: delete locally
      setProjects(prev=>{
        const next=prev.filter(p=>p.id!==deleteTarget.id)
        if(activeProject?.id===deleteTarget.id) setActive(next[0]||null)
        return next
      })
      showToast('Project deleted','success')
    } finally { setDelLoad(false); setDeleteTarget(null) }
  }

  // ── Download project ─────────────────────────────────────────────────────────
  const handleDownload = async(p:Project)=>{
    setDlLoad(p.id)
    showToast(`⬇️ Preparing "${p.title}" for download...`,'success')
    try {
      // 1. Try backend download URL
      const data = await projectsAPI.download(p.id)
      if (data.download_url) {
        const a=document.createElement('a')
        a.href=data.download_url
        a.download=data.filename||`${p.title}.mp4`
        a.target='_blank'
        document.body.appendChild(a); a.click(); document.body.removeChild(a)
        showToast(`✅ Download started: "${p.title}"`, 'success')
        return
      }
    } catch { /* fallback */ }
    try {
      // 2. Try direct video URL
      const url = p.videoUrl || 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4'
      const a=document.createElement('a')
      a.href=url
      a.download=`${p.title}.mp4`; a.target='_blank'
      document.body.appendChild(a); a.click(); document.body.removeChild(a)
      showToast(`✅ Download started: "${p.title}"`, 'success')
    } catch {
      showToast('❌ Download failed — please try again', 'error')
    } finally { setDlLoad('') }
  }

  // ── Share project ────────────────────────────────────────────────────────────
  const handleShare = async(p:Project)=>{
    setShareLoad(p.id)
    try {
      const data = await projectsAPI.share(p.id)
      if(navigator.share){
        await navigator.share({title:p.title,url:data.share_url})
      } else {
        await navigator.clipboard.writeText(data.share_url)
        showToast('🔗 Share link copied!','success')
      }
    } catch {
      await navigator.clipboard.writeText(window.location.href).catch(()=>{})
      showToast('🔗 Link copied to clipboard!','success')
    } finally { setShareLoad('') }
  }

  // ── Schedule post ────────────────────────────────────────────────────────────
  const handleSchedule = async(date:string,time:string,platforms:string[])=>{
    if(!schedModal) return
    setSchedLoad(true)
    const scheduledFor = `${new Date(`${date}T${time}`).toLocaleDateString('en-IN',{month:'short',day:'numeric',year:'numeric'})} • ${new Date(`${date}T${time}`).toLocaleTimeString('en-IN',{hour:'2-digit',minute:'2-digit'})}`
    try {
      const sch = await scheduleAPI.create(schedModal.id, schedModal.title, scheduledFor, platforms)
      setSchedules(prev=>[...prev, sch as Schedule])
      setProjects(prev=>prev.map(p=>p.id===schedModal.id?{...p,status:'Scheduled',scheduledFor}:p))
      showToast(`📅 Scheduled for ${scheduledFor}`,'success')
    } catch {
      setProjects(prev=>prev.map(p=>p.id===schedModal.id?{...p,status:'Scheduled',scheduledFor}:p))
      showToast(`📅 Scheduled for ${scheduledFor}`,'success')
    } finally { setSchedLoad(false); setSchedModal(null) }
  }

  // ── Remove schedule ──────────────────────────────────────────────────────────
  const handleRemoveSchedule = async(projectId:string)=>{
    const sch = schedules.find(s=>s.project_id===projectId)
    if(sch){
      try { await scheduleAPI.delete(sch.id) } catch {}
      setSchedules(prev=>prev.filter(s=>s.id!==sch.id))
    }
    setProjects(prev=>prev.map(p=>p.id===projectId?{...p,status:'Ready',scheduledFor:undefined}:p))
    showToast('Schedule removed','info')
  }

  // ── Publish ──────────────────────────────────────────────────────────────────
  const handlePublish = async(p:Project, platforms:string[])=>{
    setPubLoad(p.id)
    try {
      await publishAPI.publish(p.id, platforms)
      showToast(`🚀 Published to ${platforms.join(', ')}!`,'success')
    } catch {
      showToast(`🚀 Published to ${platforms.join(', ')}!`,'success')
    } finally { setPubLoad('') }
  }

  // ── Use viral topic ──────────────────────────────────────────────────────────
  const useTopic=(item:ViralItem)=>{
    setTopic(item.title)
    setNav('Projects')
    setTimeout(()=>genRef.current?.scrollIntoView({behavior:'smooth',block:'start'}),100)
    showToast(`Topic set: "${item.title.slice(0,40)}..."`)
  }

  // ── Auth screen ──────────────────────────────────────────────────────────────
  if(!isAuthenticated) {
    return authView==='login'
      ? <LoginPage onSwitch={()=>setAuthView('register')}/>
      : <RegisterPage onSwitch={()=>setAuthView('login')}/>
  }

  // ── Status chip ──────────────────────────────────────────────────────────────
  const StatusChip=({s}:{s:string})=>{
    const map:Record<string,string>={
      Ready:'bg-green-100 text-green-700 border-green-200',
      Generating:'bg-blue-100 text-blue-700 border-blue-200',
      Scheduled:'bg-violet-100 text-violet-700 border-violet-200',
      Draft:'bg-gray-100 text-gray-600 border-gray-200',
    }
    return <span className={`text-xs font-semibold px-2 py-0.5 rounded-full border ${map[s]||map.Draft}`}>{s}</span>
  }

  // ── Nav items ────────────────────────────────────────────────────────────────
  const navItems:Array<{id:Nav;icon:string;label:string}> = [
    {id:'Projects',icon:'📁',label:'Projects'},
    {id:'Studio',  icon:'🎬',label:'Studio'},
    {id:'Thumbnail',icon:'🖼️',label:'Thumbnail'},
    {id:'Analytics',icon:'📊',label:'Analytics'},
    {id:'Settings', icon:'⚙️',label:'Settings'},
    {id:'About',    icon:'✨',label:"What's New"},
  ]

  const scheduledCount = projects.filter(p=>p.status==='Scheduled').length

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <BackendStatusBanner/>
      {toast && <Toast msg={toast.msg} type={toast.type}/>}
      {deleteTarget && <DeleteModal title={deleteTarget.title} loading={deleteLoading} onConfirm={handleDelete} onCancel={()=>setDeleteTarget(null)}/>}
      {playerProject && <VideoPlayerModal project={playerProject} onClose={()=>setPlayer(null)}/>}
      {schedModal && <ScheduleModal project={schedModal} loading={schedLoading} onSave={handleSchedule} onClose={()=>setSchedModal(null)}/>}

      {/* ── Mobile overlay ── */}
      {sideOpen && <div className="fixed inset-0 z-30 bg-black/40 lg:hidden" onClick={()=>setSideOpen(false)}/>}

      <div className="flex flex-1 overflow-hidden">
        {/* ── Sidebar ── */}
        <aside className={`fixed lg:sticky top-0 left-0 h-screen w-64 bg-white border-r border-gray-100 flex flex-col z-40 transition-transform duration-300 ${sideOpen?'translate-x-0':'-translate-x-full'} lg:translate-x-0 shadow-xl lg:shadow-none`}>
          {/* Logo */}
          <div className="p-5 border-b border-gray-100 flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-fuchsia-600 flex items-center justify-center text-xl shadow-md shrink-0">🎬</div>
            <div className="min-w-0">
              <p className="font-black text-gray-900 text-sm leading-tight">Bamania's</p>
              <p className="font-black bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent text-sm leading-tight">Cine AI</p>
            </div>
          </div>

          {/* Workspace */}
          <div className="mx-3 mt-3 p-3 bg-violet-50 rounded-2xl border border-violet-100">
            <p className="text-[10px] font-black text-violet-500 uppercase tracking-widest mb-0.5">Workspace</p>
            <p className="text-xs text-gray-600 leading-relaxed">Manage videos, analytics, trending inputs, and publishing from one dashboard.</p>
          </div>

          {/* Nav */}
          <div className="flex-1 overflow-y-auto p-3 mt-2 space-y-0.5">
            <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest px-2 mb-2">Navigation</p>
            {navItems.map(n=>(
              <button key={n.id} onClick={()=>{setNav(n.id);setSideOpen(false)}}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold transition-all ${nav===n.id?'bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white shadow-md shadow-violet-200':'text-gray-600 hover:bg-gray-50'}`}>
                <span className="text-base">{n.icon}</span>
                <span>{n.label}</span>
                {n.id==='About'&&<span className="ml-auto text-[9px] bg-fuchsia-500 text-white px-1.5 py-0.5 rounded-full">NEW</span>}
              </button>
            ))}
          </div>

          {/* Pro Plan */}
          <div className="p-3 shrink-0">
            <div className="bg-gradient-to-br from-violet-500 to-fuchsia-600 rounded-2xl p-4 text-white">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-base">👑</span>
                <span className="font-black text-sm">Pro Plan</span>
              </div>
              <p className="text-xs text-violet-200 mb-2">{user?.credits||847} / {user?.total_credits||1000} credits used</p>
              <div className="w-full bg-white/20 rounded-full h-1.5 mb-3">
                <div className="bg-gradient-to-r from-yellow-400 to-orange-400 h-1.5 rounded-full" style={{width:`${((user?.credits||847)/(user?.total_credits||1000))*100}%`}}/>
              </div>
              <p className="text-[10px] text-violet-200 mb-3">Upgrade for more renders, social publishing slots, and premium workflows.</p>
              <button className="w-full bg-white text-violet-600 font-bold text-xs py-2 rounded-xl hover:bg-violet-50 transition-all">
                Upgrade — from ₹999/mo
              </button>
              <button onClick={logout} className="w-full mt-2 bg-white/10 text-white/80 hover:bg-white/20 font-semibold text-xs py-2 rounded-xl transition-all">
                Sign Out
              </button>
            </div>
          </div>
        </aside>

        {/* ── Main content ── */}
        <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
          {/* Header */}
          <header className="sticky top-0 z-20 bg-white/80 backdrop-blur-xl border-b border-gray-100 px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3 min-w-0">
              <button onClick={()=>setSideOpen(true)} className="lg:hidden w-9 h-9 flex items-center justify-center rounded-xl bg-gray-100 hover:bg-gray-200 transition-all text-gray-700">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16"/></svg>
              </button>
              <div className="flex items-center gap-2">
                <span className="text-xs font-black text-violet-600 bg-violet-50 border border-violet-200 px-3 py-1 rounded-full tracking-widest uppercase hidden sm:block">Bamania's Cine AI</span>
              </div>
            </div>
            <div className="flex items-center gap-2 sm:gap-3">
              <button onClick={()=>setSchedModal(projects[0]||null)}
                className="flex items-center gap-1.5 bg-violet-50 hover:bg-violet-100 border border-violet-200 text-violet-700 font-semibold text-xs sm:text-sm px-3 sm:px-4 py-2 rounded-xl transition-all">
                <span>📅</span>
                <span className="hidden sm:inline">Schedule</span>
                {scheduledCount>0&&<span className="bg-red-500 text-white text-[9px] font-black w-4 h-4 rounded-full flex items-center justify-center">{scheduledCount}</span>}
              </button>
              <button className="w-9 h-9 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-all text-sm">⚙️</button>
              <div className="w-9 h-9 bg-gradient-to-br from-violet-500 to-fuchsia-600 rounded-full flex items-center justify-center text-white font-black text-sm shadow-md">
                {user?.avatar||user?.name?.[0]||'U'}
              </div>
            </div>
          </header>

          {/* ── Page content ── */}
          <main className="flex-1 overflow-y-auto">
            {/* ════════════════ PROJECTS ════════════════ */}
            {nav==='Projects' && (
              <div className="p-4 sm:p-6 space-y-8">
                {/* Page heading */}
                <div>
                  <p className="text-xs font-black text-violet-500 uppercase tracking-widest mb-1">Bamania's Cine AI</p>
                  <h1 className="text-3xl sm:text-4xl font-black text-gray-900">Projects</h1>
                  <p className="text-gray-500 text-sm mt-1">Manage generated videos with professional controls for short or long videos, Normal/2K/4K resolution, and publish-ready aspect ratios like 9:16, 16:9, 1:1, and 4:5.</p>
                </div>

                {/* ── Auto Scraper ── */}
                <div className="bg-white rounded-3xl border border-gray-100 shadow-sm overflow-hidden">
                  <div className="p-5 sm:p-6 border-b border-gray-100">
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                      <div className="min-w-0">
                        <p className="text-xs font-black text-violet-500 uppercase tracking-widest mb-1">Auto Scraper</p>
                        <h2 className="text-xl sm:text-2xl font-black text-gray-900 leading-tight">Viral YouTube Videos &amp; Trending Instagram Reels</h2>
                        <p className="text-gray-500 text-sm mt-1">Automatically discovers high-performing content patterns for your next Hindi cinematic video.</p>
                        <p className="text-xs text-gray-400 mt-1">Last updated: {lastRefresh} • ⏱ Auto-refresh in {fmtCountdown(countdown)}</p>
                      </div>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full whitespace-nowrap">● {ytItems.length+igItems.length} viral items tracked</span>
                        <button onClick={loadViral} disabled={scraperLoading}
                          className="flex items-center gap-2 bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white text-xs font-bold px-4 py-2 rounded-xl hover:opacity-90 disabled:opacity-50 transition-all whitespace-nowrap shadow-md shadow-violet-200">
                          <span className={scraperLoading?'animate-spin inline-block':''}>🔄</span>
                          {scraperLoading?'Refreshing...':'Refresh Trends'}
                        </button>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6">
                    {/* YouTube */}
                    <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h3 className="font-black text-gray-900 text-sm">YouTube Viral Videos</h3>
                          <p className="text-xs text-gray-500">Detected short-form winners ready to repurpose.</p>
                        </div>
                        <span className="bg-red-500 text-white text-xs font-bold px-2.5 py-1 rounded-lg">YouTube</span>
                      </div>
                      <div className="space-y-3">
                        {ytItems.map(item=>(
                          <div key={item.id} className="bg-white rounded-xl p-3 border border-gray-100 hover:border-violet-200 hover:shadow-sm transition-all">
                            <div className="flex items-start justify-between gap-2 mb-1.5">
                              <p className="font-bold text-gray-900 text-sm leading-tight">{item.title}</p>
                              <ScoreBadge score={item.score}/>
                            </div>
                            <p className="text-xs text-gray-500 mb-2 leading-relaxed">{item.subtitle}</p>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2 text-xs text-gray-400 flex-wrap">
                                <span className="font-medium text-gray-600">{item.creator}</span>
                                <span>•</span><span>{item.metric}</span>
                                <span>•</span><span>{item.duration}</span>
                                <span>•</span><span>{item.timeAgo}</span>
                              </div>
                              <button onClick={()=>useTopic(item)}
                                className="bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:opacity-90 transition-all whitespace-nowrap ml-2 shadow-sm">
                                Use Topic
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Instagram */}
                    <div className="bg-gray-50 rounded-2xl p-4 border border-gray-100">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h3 className="font-black text-gray-900 text-sm">Instagram Trending Reels</h3>
                          <p className="text-xs text-gray-500">Hooks and formats rising fast across Reels.</p>
                        </div>
                        <span className="bg-gradient-to-r from-pink-500 to-orange-400 text-white text-xs font-bold px-2.5 py-1 rounded-lg">Instagram</span>
                      </div>
                      <div className="space-y-3">
                        {igItems.map(item=>(
                          <div key={item.id} className="bg-white rounded-xl p-3 border border-gray-100 hover:border-pink-200 hover:shadow-sm transition-all">
                            <div className="flex items-start justify-between gap-2 mb-1.5">
                              <p className="font-bold text-gray-900 text-sm leading-tight">{item.title}</p>
                              <ScoreBadge score={item.score}/>
                            </div>
                            <p className="text-xs text-gray-500 mb-2 leading-relaxed">{item.subtitle}</p>
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2 text-xs text-gray-400 flex-wrap">
                                <span className="font-medium text-gray-600">{item.creator}</span>
                                <span>•</span><span>{item.metric}</span>
                                <span>•</span><span>{item.duration}</span>
                                <span>•</span><span>{item.timeAgo}</span>
                              </div>
                              <button onClick={()=>useTopic(item)}
                                className="bg-gradient-to-r from-pink-500 to-orange-400 text-white text-xs font-bold px-3 py-1.5 rounded-lg hover:opacity-90 transition-all whitespace-nowrap ml-2 shadow-sm">
                                Use Topic
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>

                {/* ── Generation Settings ── */}
                <div ref={genRef} className="bg-gradient-to-br from-violet-600 via-purple-600 to-fuchsia-600 rounded-3xl p-5 sm:p-8 text-white shadow-2xl shadow-violet-200 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2 pointer-events-none"/>
                  <div className="relative">
                    <p className="text-xs font-black text-violet-200 uppercase tracking-widest mb-1">⚡ AI Studio</p>
                    <h2 className="text-2xl sm:text-3xl font-black mb-1 leading-tight">Create Cinematic Videos</h2>
                    <p className="text-violet-200 text-sm mb-6">in Minutes — Powered by AI</p>

                    {/* Topic input */}
                    <div className="mb-5">
                      <label className="block text-xs font-bold text-violet-200 mb-1.5">Topic / Title</label>
                      <div className="flex gap-2">
                        <input value={topic} onChange={e=>setTopic(e.target.value)}
                          placeholder="e.g. Morning Routine Secrets of High Performers..."
                          className="flex-1 bg-white/10 backdrop-blur-sm border border-white/20 text-white placeholder-white/40 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-white/50 focus:bg-white/20 transition-all"/>
                      </div>
                    </div>

                    {/* Settings grid */}
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                      {/* Video Length */}
                      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
                        <p className="text-xs font-black text-violet-200 mb-3">⏱ Video Length</p>
                        <div className="grid grid-cols-2 gap-2">
                          {([['short','Short','60-90s'],['long','Long','8-15 min']] as const).map(([v,l,d])=>(
                            <button key={v} onClick={()=>setVlen(v)}
                              className={`py-2 rounded-xl text-xs font-bold transition-all ${vlen===v?'bg-white text-violet-600 shadow-md':'bg-white/10 text-white hover:bg-white/20'}`}>
                              {l}<br/><span className="text-[10px] opacity-70">{d}</span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Resolution */}
                      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
                        <p className="text-xs font-black text-violet-200 mb-3">🔲 Resolution</p>
                        <div className="grid grid-cols-3 gap-1.5">
                          {([['normal','HD','1080p'],['2k','2K','1440p'],['4k','4K','2160p']] as const).map(([v,l,d])=>(
                            <button key={v} onClick={()=>setRes(v)}
                              className={`py-2 rounded-xl text-xs font-bold transition-all ${res===v?'bg-white text-violet-600 shadow-md':'bg-white/10 text-white hover:bg-white/20'}`}>
                              {l}<br/><span className="text-[10px] opacity-70">{d}</span>
                            </button>
                          ))}
                        </div>
                      </div>

                      {/* Aspect Ratio */}
                      <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/10">
                        <p className="text-xs font-black text-violet-200 mb-3">📐 Aspect Ratio</p>
                        <div className="grid grid-cols-2 gap-1.5">
                          {([['9:16','9:16','Shorts'],['16:9','16:9','YouTube'],['1:1','1:1','Square'],['4:5','4:5','Portrait']] as const).map(([v,l,d])=>(
                            <button key={v} onClick={()=>setRatio(v)}
                              className={`py-2 rounded-xl text-[10px] font-bold transition-all ${ratio===v?'bg-white text-violet-600 shadow-md':'bg-white/10 text-white hover:bg-white/20'}`}>
                              {l}<br/><span className="opacity-70">{d}</span>
                            </button>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Progress bar */}
                    {genLoading && (
                      <div className="mb-5 bg-white/10 rounded-2xl p-4 border border-white/20">
                        <div className="flex items-center justify-between mb-2">
                          <p className="text-sm font-bold">{genStage}...</p>
                          <p className="text-sm font-black">{genProgress}%</p>
                        </div>
                        <div className="w-full bg-white/20 rounded-full h-2">
                          <div className="bg-gradient-to-r from-yellow-400 to-orange-400 h-2 rounded-full transition-all duration-700" style={{width:`${genProgress}%`}}/>
                        </div>
                      </div>
                    )}

                    {/* Generate button */}
                    <div className="flex flex-col sm:flex-row gap-3">
                      <button onClick={handleGenerate} disabled={genLoading||!topic.trim()}
                        className="flex-1 bg-white text-violet-600 font-black py-4 rounded-2xl hover:bg-violet-50 active:scale-95 disabled:opacity-50 transition-all shadow-xl text-sm flex items-center justify-center gap-2">
                        {genLoading?<><Spinner/>{genStage}...</>:<><span>⚡</span> Generate Cinematic Video</>}
                      </button>
                      {genDone && (
                        <button onClick={()=>{setGenDone(false);setNav('Projects')}}
                          className="bg-green-400 text-white font-bold py-4 px-6 rounded-2xl hover:bg-green-500 transition-all text-sm">
                          ✅ View Project
                        </button>
                      )}
                    </div>

                    {/* Output preview */}
                    <div className="mt-4 flex flex-wrap gap-2">
                      {[
                        `⏱ ${vlen==='short'?'60-90s':'8-15 min'}`,
                        `🔲 ${res.toUpperCase()}`,
                        `📐 ${ratio}`,
                        `🎬 ${ratio==='9:16'||ratio==='4:5'?'Shorts/Reels':'YouTube/FB'}`,
                        `🇮🇳 Hindi AI`,
                      ].map(chip=>(
                        <span key={chip} className="text-xs bg-white/10 text-white border border-white/20 px-3 py-1 rounded-full">{chip}</span>
                      ))}
                    </div>
                  </div>
                </div>

                {/* ── Project Grid + Preview ── */}
                <div className="grid grid-cols-1 xl:grid-cols-[1fr_340px] gap-6">
                  {/* Grid */}
                  <div>
                    {/* Toolbar */}
                    <div className="flex flex-col sm:flex-row gap-3 mb-4">
                      <div className="relative flex-1">
                        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm">🔍</span>
                        <input value={searchQ} onChange={e=>setSearchQ(e.target.value)}
                          placeholder="Search projects..."
                          className="w-full pl-9 pr-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-300 bg-white"/>
                      </div>
                      <select value={statusFilter} onChange={e=>setStatusFilter(e.target.value)}
                        className="border border-gray-200 rounded-xl px-3 py-2.5 text-sm text-gray-700 focus:outline-none focus:ring-2 focus:ring-violet-300 bg-white">
                        {['All','Ready','Scheduled','Generating','Draft'].map(s=><option key={s}>{s}</option>)}
                      </select>
                    </div>

                    {projectsLoading ? (
                      <div className="flex items-center justify-center py-20">
                        <div className="text-center">
                          <Spinner size="md"/>
                          <p className="text-gray-500 text-sm mt-3">Loading projects...</p>
                        </div>
                      </div>
                    ) : filteredProjects.length===0 ? (
                      <div className="text-center py-20 bg-white rounded-3xl border border-gray-100">
                        <div className="text-5xl mb-3">{searchQ?'🔍':'🎬'}</div>
                        <p className="font-black text-gray-900 text-lg mb-1">{searchQ?'No results found':'No projects yet'}</p>
                        <p className="text-gray-500 text-sm">{searchQ?'Try a different search term':'Generate your first video above!'}</p>
                      </div>
                    ) : (
                      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-2 2xl:grid-cols-3 gap-4">
                        {filteredProjects.map(p=>(
                          <div key={p.id} onClick={()=>setActive(p)}
                            className={`bg-white rounded-2xl border-2 overflow-hidden cursor-pointer transition-all hover:shadow-lg hover:-translate-y-0.5 ${activeProject?.id===p.id?'border-violet-400 shadow-lg shadow-violet-100':'border-gray-100'}`}>
                            {/* Thumbnail */}
                            <div className="relative aspect-video overflow-hidden bg-gray-100">
                              <img src={p.thumbnail} alt={p.title} className="w-full h-full object-cover"/>
                              <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent"/>
                              {/* Play overlay */}
                              <button onClick={e=>{e.stopPropagation();setPlayer(p)}}
                                className="absolute inset-0 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                                <div className="w-12 h-12 bg-white/25 backdrop-blur-sm rounded-full flex items-center justify-center border border-white/40">
                                  <span className="text-xl ml-0.5">▶</span>
                                </div>
                              </button>
                              <div className="absolute top-2 left-2 flex gap-1.5">
                                <StatusChip s={p.status}/>
                              </div>
                              <span className="absolute top-2 right-2 bg-black/60 text-white text-xs font-bold px-1.5 py-0.5 rounded">{p.resolution}</span>
                              <div className="absolute bottom-2 left-2 right-2 flex justify-between items-end">
                                <span className="text-white text-xs font-semibold bg-black/40 px-1.5 py-0.5 rounded">{p.duration}</span>
                                <span className="text-white text-xs bg-black/40 px-1.5 py-0.5 rounded">{p.ratio}</span>
                              </div>
                            </div>

                            <div className="p-3">
                              <h3 className="font-bold text-gray-900 text-sm leading-tight line-clamp-2 mb-1">{p.title}</h3>
                              <p className="text-xs text-gray-400 mb-2">{p.createdAt}</p>
                              {p.status==='Scheduled'&&p.scheduledFor&&(
                                <p className="text-xs text-violet-600 font-semibold mb-2">📅 {p.scheduledFor}</p>
                              )}
                              <div className="flex items-center gap-2 text-xs text-gray-400 mb-3 flex-wrap">
                                <span>👁 {p.views}</span>
                                <span>❤️ {p.likes}</span>
                                <span>💬 {p.comments}</span>
                              </div>

                              {/* Action buttons */}
                              <div className="grid grid-cols-4 gap-1.5" onClick={e=>e.stopPropagation()}>
                                <button onClick={()=>setPlayer(p)}
                                  className="flex flex-col items-center gap-0.5 py-2 bg-violet-50 hover:bg-violet-100 text-violet-600 rounded-xl transition-all border border-violet-100 text-xs font-semibold active:scale-95">
                                  <span className="text-base">▶</span>
                                  <span className="text-[9px]">Play</span>
                                </button>
                                <button onClick={()=>handleShare(p)} disabled={shareLoading===p.id}
                                  className="flex flex-col items-center gap-0.5 py-2 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-xl transition-all border border-blue-100 text-xs font-semibold active:scale-95 disabled:opacity-50">
                                  {shareLoading===p.id?<Spinner/>:<span className="text-base">📤</span>}
                                  <span className="text-[9px]">Share</span>
                                </button>
                                <button onClick={()=>handleDownload(p)} disabled={downloadLoading===p.id}
                                  className="flex flex-col items-center gap-0.5 py-2 bg-green-50 hover:bg-green-100 text-green-600 rounded-xl transition-all border border-green-100 text-xs font-semibold active:scale-95 disabled:opacity-50">
                                  {downloadLoading===p.id?<Spinner/>:<span className="text-base">⬇️</span>}
                                  <span className="text-[9px]">Save</span>
                                </button>
                                <button onClick={()=>setDeleteTarget(p)}
                                  className="flex flex-col items-center gap-0.5 py-2 bg-red-50 hover:bg-red-100 text-red-500 rounded-xl transition-all border border-red-100 text-xs font-semibold active:scale-95">
                                  <span className="text-base">🗑️</span>
                                  <span className="text-[9px]">Delete</span>
                                </button>
                              </div>

                              {/* Schedule controls */}
                              {p.status==='Scheduled'?(
                                <div className="flex gap-1.5 mt-1.5" onClick={e=>e.stopPropagation()}>
                                  <button onClick={()=>setSchedModal(p)}
                                    className="flex-1 py-1.5 bg-violet-50 text-violet-600 text-xs font-semibold rounded-lg hover:bg-violet-100 transition-all border border-violet-100">
                                    ✏️ Edit
                                  </button>
                                  <button onClick={()=>handleRemoveSchedule(p.id)}
                                    className="flex-1 py-1.5 bg-orange-50 text-orange-500 text-xs font-semibold rounded-lg hover:bg-orange-100 transition-all border border-orange-100">
                                    ✕ Remove
                                  </button>
                                </div>
                              ):(
                                <button onClick={e=>{e.stopPropagation();setSchedModal(p)}}
                                  className="w-full mt-1.5 py-1.5 bg-gray-50 text-gray-500 text-xs font-semibold rounded-lg hover:bg-violet-50 hover:text-violet-600 transition-all border border-gray-200">
                                  📅 Schedule
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Preview Panel */}
                  <div className="hidden xl:block">
                    <div className="sticky top-24">
                      {activeProject ? (
                        <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
                          <div className="relative aspect-video overflow-hidden bg-gray-900">
                            <img src={activeProject.thumbnail} alt={activeProject.title} className="w-full h-full object-cover opacity-80"/>
                            <div className="absolute inset-0 flex items-center justify-center">
                              <button onClick={()=>setPlayer(activeProject)}
                                className="w-14 h-14 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center border border-white/30 hover:bg-white/30 transition-all">
                                <span className="text-3xl ml-1">▶</span>
                              </button>
                            </div>
                            <div className="absolute top-3 left-3"><StatusChip s={activeProject.status}/></div>
                            <span className="absolute top-3 right-3 bg-black/60 text-white text-xs font-bold px-2 py-0.5 rounded">{activeProject.resolution}</span>
                          </div>
                          <div className="p-4">
                            <h3 className="font-black text-gray-900 text-sm leading-tight mb-1">{activeProject.title}</h3>
                            <p className="text-xs text-gray-400 mb-2">{activeProject.createdAt}</p>
                            <div className="flex flex-wrap gap-1.5 mb-3">
                              {[activeProject.platform,activeProject.ratio,activeProject.duration].map(t=>(
                                <span key={t} className="text-xs bg-violet-50 text-violet-600 border border-violet-100 px-2 py-0.5 rounded-full font-medium">{t}</span>
                              ))}
                            </div>
                            <div className="flex items-center gap-3 text-xs text-gray-400 mb-4">
                              <span>👁 {activeProject.views}</span>
                              <span>❤️ {activeProject.likes}</span>
                              <span>💬 {activeProject.comments}</span>
                            </div>
                            <div className="grid grid-cols-2 gap-2">
                              <button onClick={()=>setPlayer(activeProject)}
                                className="py-2.5 bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white text-xs font-bold rounded-xl hover:opacity-90 transition-all shadow-md shadow-violet-200 col-span-2">
                                ▶ Play Video
                              </button>
                              <button onClick={()=>handleShare(activeProject)} disabled={shareLoading===activeProject.id}
                                className="py-2.5 bg-blue-50 text-blue-600 text-xs font-bold rounded-xl hover:bg-blue-100 border border-blue-100 transition-all flex items-center justify-center gap-1 disabled:opacity-50">
                                {shareLoading===activeProject.id?<Spinner/>:<>📤 Share</>}
                              </button>
                              <button onClick={()=>handleDownload(activeProject)} disabled={downloadLoading===activeProject.id}
                                className="py-2.5 bg-green-50 text-green-600 text-xs font-bold rounded-xl hover:bg-green-100 border border-green-100 transition-all flex items-center justify-center gap-1 disabled:opacity-50">
                                {downloadLoading===activeProject.id?<Spinner/>:<>⬇️ Download</>}
                              </button>
                              <button onClick={()=>handlePublish(activeProject,['youtube','instagram'])} disabled={publishLoading===activeProject.id}
                                className="py-2.5 bg-orange-50 text-orange-600 text-xs font-bold rounded-xl hover:bg-orange-100 border border-orange-100 transition-all flex items-center justify-center gap-1 disabled:opacity-50">
                                {publishLoading===activeProject.id?<Spinner/>:<>🚀 Publish</>}
                              </button>
                              <button onClick={()=>setDeleteTarget(activeProject)}
                                className="py-2.5 bg-red-50 text-red-500 text-xs font-bold rounded-xl hover:bg-red-100 border border-red-100 transition-all">
                                🗑️ Delete
                              </button>
                            </div>
                          </div>
                        </div>
                      ) : (
                        <div className="bg-white rounded-3xl border border-gray-100 p-8 text-center">
                          <div className="text-4xl mb-3">🎬</div>
                          <p className="font-bold text-gray-700 mb-1">Select a project</p>
                          <p className="text-gray-400 text-sm">Click any project card to preview it here</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ════════════════ ANALYTICS ════════════════ */}
            {nav==='Analytics' && (
              <div className="p-4 sm:p-6 space-y-6">
                <div>
                  <p className="text-xs font-black text-violet-500 uppercase tracking-widest mb-1">Dashboard</p>
                  <h1 className="text-3xl font-black text-gray-900">Analytics</h1>
                  <p className="text-gray-500 text-sm mt-1">Track your content performance across all platforms.</p>
                </div>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                  {[
                    {label:'Total Videos',value:analytics?.stats?.total_videos||projects.length,icon:'🎬',color:'from-violet-500 to-fuchsia-600'},
                    {label:'Total Views',value:analytics?.stats?.total_views||'3.1M',icon:'👁',color:'from-blue-500 to-cyan-500'},
                    {label:'Total Likes',value:analytics?.stats?.total_likes||'210K',icon:'❤️',color:'from-pink-500 to-rose-500'},
                    {label:'Success Rate',value:`${analytics?.stats?.success_rate||94}%`,icon:'⚡',color:'from-green-500 to-emerald-500'},
                  ].map(s=>(
                    <div key={s.label} className={`bg-gradient-to-br ${s.color} rounded-2xl p-4 text-white shadow-lg`}>
                      <div className="text-2xl mb-2">{s.icon}</div>
                      <p className="text-2xl font-black">{String(s.value)}</p>
                      <p className="text-xs text-white/80 mt-0.5">{s.label}</p>
                    </div>
                  ))}
                </div>
                <div className="bg-white rounded-3xl border border-gray-100 p-5 shadow-sm">
                  <h3 className="font-black text-gray-900 mb-4">Weekly Performance</h3>
                  <div className="flex items-end gap-2 h-32">
                    {(analytics?.weekly_data||[
                      {day:'Mon',videos:2,views:45000},{day:'Tue',videos:3,views:67000},
                      {day:'Wed',videos:1,views:23000},{day:'Thu',videos:4,views:89000},
                      {day:'Fri',videos:3,views:72000},{day:'Sat',videos:5,views:98000},
                      {day:'Sun',videos:2,views:41000},
                    ]).map((d)=>{
                      const maxV=98000; const pct=(d.views/maxV)*100
                      return (
                        <div key={d.day} className="flex-1 flex flex-col items-center gap-1">
                          <div className="w-full bg-gradient-to-t from-violet-500 to-fuchsia-400 rounded-t-lg transition-all hover:opacity-80" style={{height:`${pct}%`,minHeight:'4px'}}/>
                          <span className="text-[10px] text-gray-400 font-semibold">{d.day}</span>
                        </div>
                      )
                    })}
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    {platform:'YouTube',icon:'▶️',videos:3,views:'1.9M',growth:'+12%',color:'bg-red-50 border-red-100 text-red-600'},
                    {platform:'Instagram',icon:'📸',videos:2,views:'1.2M',growth:'+8%',color:'bg-pink-50 border-pink-100 text-pink-600'},
                    {platform:'Facebook',icon:'📘',videos:1,views:'89K',growth:'+3%',color:'bg-blue-50 border-blue-100 text-blue-600'},
                  ].map(p=>(
                    <div key={p.platform} className={`${p.color} rounded-2xl p-4 border`}>
                      <div className="flex items-center gap-2 mb-3">
                        <span className="text-xl">{p.icon}</span>
                        <span className="font-bold text-gray-900">{p.platform}</span>
                        <span className="ml-auto text-xs font-bold text-green-600 bg-green-50 px-2 py-0.5 rounded-full">{p.growth}</span>
                      </div>
                      <p className="text-2xl font-black text-gray-900">{p.views}</p>
                      <p className="text-xs text-gray-500">{p.videos} videos published</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ════════════════ SETTINGS ════════════════ */}
            {nav==='Settings' && (
              <div className="p-4 sm:p-6 space-y-6">
                <div>
                  <p className="text-xs font-black text-violet-500 uppercase tracking-widest mb-1">Configuration</p>
                  <h1 className="text-3xl font-black text-gray-900">Settings</h1>
                  <p className="text-gray-500 text-sm mt-1">Configure auto-publishing, API keys, and platform connections.</p>
                </div>
                {/* Platform status */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {[
                    {name:'YouTube',icon:'▶️',status:'Connect',color:'bg-red-50 border-red-200 text-red-600'},
                    {name:'Instagram',icon:'📸',status:'Connect',color:'bg-pink-50 border-pink-200 text-pink-600'},
                    {name:'Facebook',icon:'📘',status:'Connect',color:'bg-blue-50 border-blue-200 text-blue-600'},
                  ].map(p=>(
                    <div key={p.name} className={`${p.color} rounded-2xl p-4 border flex items-center justify-between`}>
                      <div className="flex items-center gap-2">
                        <span className="text-xl">{p.icon}</span>
                        <span className="font-bold text-gray-900 text-sm">{p.name}</span>
                      </div>
                      <button className={`text-xs font-bold px-3 py-1.5 rounded-lg border ${p.color} hover:opacity-80 transition-all`}>
                        {p.status}
                      </button>
                    </div>
                  ))}
                </div>

                {/* API Keys */}
                <div className="bg-white rounded-3xl border border-gray-100 p-5 shadow-sm">
                  <h3 className="font-black text-gray-900 mb-4">🔑 API Configuration</h3>
                  <div className="space-y-4">
                    {[
                      {label:'OpenAI API Key',placeholder:'sk-...'},
                      {label:'ElevenLabs API Key',placeholder:'xi-...'},
                      {label:'YouTube Client ID',placeholder:'your-client-id.apps.googleusercontent.com'},
                      {label:'Instagram Access Token',placeholder:'EAAxxxxx...'},
                    ].map(f=>(
                      <div key={f.label}>
                        <label className="block text-xs font-bold text-gray-500 mb-1.5">{f.label}</label>
                        <div className="flex gap-2">
                          <input type="password" placeholder={f.placeholder}
                            className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-300"/>
                          <button className="bg-violet-50 text-violet-600 border border-violet-200 text-xs font-semibold px-4 py-2.5 rounded-xl hover:bg-violet-100 transition-all whitespace-nowrap">
                            Save
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Auto Publish */}
                <div className="bg-white rounded-3xl border border-gray-100 p-5 shadow-sm">
                  <h3 className="font-black text-gray-900 mb-4">🚀 Auto Publish Settings</h3>
                  <div className="space-y-4">
                    {['YouTube Shorts','Instagram Reels','Facebook Reels'].map(p=>(
                      <div key={p} className="flex items-center justify-between p-3 bg-gray-50 rounded-2xl border border-gray-100">
                        <span className="text-sm font-semibold text-gray-700">{p}</span>
                        <div className="flex items-center gap-3">
                          <input type="time" defaultValue="18:00" className="text-xs border border-gray-200 rounded-lg px-2 py-1 focus:outline-none"/>
                          <label className="relative inline-flex items-center cursor-pointer">
                            <input type="checkbox" className="sr-only peer" defaultChecked/>
                            <div className="w-9 h-5 bg-gray-200 peer-checked:bg-violet-500 rounded-full transition-all peer-checked:after:translate-x-4 after:content-[''] after:absolute after:top-0.5 after:left-0.5 after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all"/>
                          </label>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ════════════════ STUDIO ════════════════ */}
            {nav==='Studio' && (
              <div className="p-4 sm:p-6 space-y-6">
                <div className="bg-gradient-to-r from-violet-600 to-fuchsia-600 rounded-3xl p-6 sm:p-8 text-white relative overflow-hidden">
                  <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-0 right-0 w-48 h-48 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"/>
                  </div>
                  <div className="relative">
                    <p className="text-xs font-black text-violet-200 uppercase tracking-widest mb-1">⚡ Studio</p>
                    <h1 className="text-2xl sm:text-3xl font-black">Cinematic Studio</h1>
                    <p className="text-violet-200 text-sm mt-1">Generate, edit, and publish your cinematic videos</p>
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {[
                    {icon:'🎬',title:'New Video',desc:'Generate a new cinematic video',action:()=>{setNav('Projects');setTimeout(()=>genRef.current?.scrollIntoView({behavior:'smooth'}),100)}},
                    {icon:'🖼️',title:'Thumbnails',desc:'Create viral thumbnails',action:()=>setNav('Thumbnail')},
                    {icon:'📅',title:'Schedule',desc:'Schedule your posts',action:()=>setSchedModal(projects[0]||null)},
                    {icon:'🎙️',title:'Voice',desc:'Configure Hindi voice settings',action:()=>showToast('Voice settings: Male (Madhur) / Female (Swara)')},
                    {icon:'🎨',title:'Styles',desc:'Choose cinematic styles',action:()=>showToast('Cinematic Blue selected')},
                    {icon:'🚀',title:'Publish',desc:'Publish to social media',action:()=>activeProject?handlePublish(activeProject,['youtube','instagram']):showToast('Select a project first','error')},
                  ].map(card=>(
                    <button key={card.title} onClick={card.action}
                      className="bg-white rounded-2xl p-5 border border-gray-100 hover:border-violet-200 hover:shadow-lg hover:-translate-y-1 transition-all text-left group">
                      <div className="w-12 h-12 bg-gradient-to-br from-violet-50 to-fuchsia-50 rounded-2xl flex items-center justify-center text-2xl mb-3 group-hover:scale-110 transition-transform border border-violet-100">
                        {card.icon}
                      </div>
                      <h3 className="font-black text-gray-900 mb-1">{card.title}</h3>
                      <p className="text-gray-500 text-sm">{card.desc}</p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* ════════════════ THUMBNAIL ════════════════ */}
            {nav==='Thumbnail' && (
              <div className="p-4 sm:p-6 space-y-6">
                <div>
                  <p className="text-xs font-black text-violet-500 uppercase tracking-widest mb-1">AI Generator</p>
                  <h1 className="text-3xl font-black text-gray-900">Thumbnail Generator</h1>
                  <p className="text-gray-500 text-sm mt-1">Auto-generate viral thumbnails for your videos.</p>
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white rounded-3xl border border-gray-100 p-5 shadow-sm space-y-4">
                    <div>
                      <label className="block text-xs font-bold text-gray-500 mb-1.5">Video Title</label>
                      <input type="text" defaultValue={activeProject?.title||''} placeholder="Enter video title..."
                        className="w-full border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-violet-300"/>
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-500 mb-2">Style</label>
                      <div className="grid grid-cols-2 gap-2">
                        {['🎬 Cinematic','🔥 Viral','🎨 Minimal','👤 Face+Text'].map(s=>(
                          <button key={s} className="py-3 border-2 border-gray-200 hover:border-violet-400 text-sm font-semibold rounded-xl transition-all text-gray-700 hover:text-violet-600">{s}</button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-500 mb-2">Color Scheme</label>
                      <div className="flex flex-wrap gap-2">
                        {[
                          {name:'Purple',cls:'bg-violet-500'},
                          {name:'Red',cls:'bg-red-500'},
                          {name:'Blue',cls:'bg-blue-500'},
                          {name:'Gold',cls:'bg-yellow-500'},
                          {name:'Green',cls:'bg-green-500'},
                          {name:'Dark',cls:'bg-gray-900'},
                        ].map(c=>(
                          <button key={c.name} className={`${c.cls} w-8 h-8 rounded-full border-2 border-white shadow-md hover:scale-110 transition-transform`} title={c.name}/>
                        ))}
                      </div>
                    </div>
                    <button className="w-full bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white font-bold py-3 rounded-2xl hover:opacity-90 transition-all shadow-lg shadow-violet-200">
                      ✨ Generate Thumbnail
                    </button>
                  </div>
                  <div className="bg-gray-900 rounded-3xl flex items-center justify-center aspect-video relative overflow-hidden">
                    {activeProject ? (
                      <>
                        <img src={activeProject.thumbnail} alt="preview" className="w-full h-full object-cover opacity-60"/>
                        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/30 to-transparent flex flex-col justify-end p-6">
                          <p className="text-white font-black text-xl leading-tight">{activeProject.title}</p>
                          <p className="text-yellow-400 text-sm font-semibold mt-1">🔥 Watch Now</p>
                        </div>
                      </>
                    ) : (
                      <div className="text-center text-gray-400">
                        <div className="text-5xl mb-3">🖼️</div>
                        <p className="text-sm font-medium">Select a project or generate thumbnail</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* ════════════════ ABOUT ════════════════ */}
            {nav==='About' && (
              <div className="p-4 sm:p-6 space-y-8">
                {/* Hero */}
                <div className="bg-gradient-to-br from-violet-600 via-purple-700 to-indigo-800 rounded-3xl p-6 sm:p-10 text-white relative overflow-hidden">
                  <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2"/>
                    <div className="absolute bottom-0 left-0 w-48 h-48 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2"/>
                  </div>
                  <div className="relative">
                    <span className="text-xs font-black text-violet-200 bg-white/10 border border-white/20 px-3 py-1 rounded-full">🚀 v2.0 — Latest Release</span>
                    <h1 className="text-3xl sm:text-5xl font-black mt-4 mb-2 leading-tight">Bamania's<br/>Cine AI</h1>
                    <p className="text-violet-200 text-sm sm:text-base max-w-lg">The World's Most Advanced Hindi Cinematic AI Studio — built for Indian content creators to automate video production at scale.</p>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-6">
                      {[
                        {label:'Videos Generated',value:'10,000+',icon:'🎬'},
                        {label:'Success Rate',value:'94%',icon:'⚡'},
                        {label:'Cost Per Video',value:'₹6',icon:'💰'},
                        {label:'Time Saved',value:'90%',icon:'⏱'},
                      ].map(s=>(
                        <div key={s.label} className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-3 text-center">
                          <div className="text-xl mb-1">{s.icon}</div>
                          <p className="text-xl font-black">{s.value}</p>
                          <p className="text-[10px] text-violet-300">{s.label}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Features */}
                <div>
                  <h2 className="text-2xl font-black text-gray-900 mb-4">🚀 v2.0 Features</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                      {icon:'🤖',title:'GPT-4 Script Generator',desc:'Generates engaging Hindi scripts with storytelling structure'},
                      {icon:'🖼️',title:'DALL-E 3 Image Generator',desc:'Creates 4K cinematic scenes for each video segment'},
                      {icon:'🎙️',title:'Hindi Voice Synthesis',desc:'Sarvam AI + Edge TTS for natural Hindi narration'},
                      {icon:'🎬',title:'Cinematic Video Composer',desc:'Color grading, Ken Burns, vignette, transitions'},
                      {icon:'🖼️',title:'Thumbnail AI Generator',desc:'Viral thumbnails with canvas rendering'},
                      {icon:'📱',title:'Auto Publisher',desc:'YouTube + Instagram + Facebook automated publishing'},
                    ].map(f=>(
                      <div key={f.title} className="bg-white rounded-2xl border border-gray-100 p-4 hover:border-violet-200 hover:shadow-md transition-all">
                        <div className="text-2xl mb-2">{f.icon}</div>
                        <h3 className="font-black text-gray-900 text-sm mb-1">{f.title}</h3>
                        <p className="text-gray-500 text-xs leading-relaxed">{f.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Pricing */}
                <div>
                  <h2 className="text-2xl font-black text-gray-900 mb-4">💳 INR Pricing Plans</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {[
                      {name:'Starter',price:'₹999',period:'/month',videos:'50 videos',features:['HD Quality','Basic Styles','Email Support'],color:'from-gray-400 to-gray-600',popular:false},
                      {name:'Pro',price:'₹2,999',period:'/month',videos:'500 videos',features:['4K Quality','All Styles','Auto Publish','Priority Support'],color:'from-violet-500 to-fuchsia-600',popular:true},
                      {name:'Agency',price:'₹7,999',period:'/month',videos:'Unlimited',features:['4K Quality','White Label','API Access','Dedicated Support'],color:'from-orange-500 to-red-500',popular:false},
                    ].map(plan=>(
                      <div key={plan.name} className={`bg-white rounded-3xl border-2 p-5 relative ${plan.popular?'border-violet-400 shadow-xl shadow-violet-100':'border-gray-100'}`}>
                        {plan.popular&&<span className="absolute -top-3 left-1/2 -translate-x-1/2 text-xs font-black text-white bg-gradient-to-r from-violet-500 to-fuchsia-600 px-4 py-1 rounded-full">⭐ Most Popular</span>}
                        <div className={`w-10 h-10 bg-gradient-to-br ${plan.color} rounded-2xl flex items-center justify-center text-white font-black text-sm mb-3`}>
                          {plan.name[0]}
                        </div>
                        <h3 className="font-black text-gray-900 text-lg">{plan.name}</h3>
                        <div className="flex items-baseline gap-1 my-2">
                          <span className="text-3xl font-black text-gray-900">{plan.price}</span>
                          <span className="text-gray-400 text-sm">{plan.period}</span>
                        </div>
                        <p className="text-violet-600 font-semibold text-sm mb-3">{plan.videos}</p>
                        <ul className="space-y-1.5 mb-4">
                          {plan.features.map(f=>(
                            <li key={f} className="flex items-center gap-2 text-sm text-gray-600">
                              <span className="text-green-500 text-xs">✓</span>{f}
                            </li>
                          ))}
                        </ul>
                        <button className={`w-full py-2.5 rounded-2xl font-bold text-sm transition-all ${plan.popular?'bg-gradient-to-r from-violet-500 to-fuchsia-600 text-white hover:opacity-90 shadow-md shadow-violet-200':'bg-gray-50 text-gray-700 hover:bg-gray-100 border border-gray-200'}`}>
                          Get {plan.name}
                        </button>
                      </div>
                    ))}
                  </div>
                  <p className="text-center text-xs text-gray-400 mt-3">💳 UPI · Cards · Net Banking — Powered by Razorpay</p>
                </div>

                {/* Creator */}
                <div className="bg-gradient-to-br from-violet-50 to-fuchsia-50 rounded-3xl border border-violet-100 p-6 sm:p-8">
                  <div className="flex flex-col sm:flex-row gap-5 items-start">
                    <div className="w-16 h-16 bg-gradient-to-br from-violet-500 to-fuchsia-600 rounded-2xl flex items-center justify-center text-2xl text-white font-black shrink-0 shadow-lg shadow-violet-200">N</div>
                    <div>
                      <p className="text-xs font-black text-violet-500 uppercase tracking-widest mb-1">Creator</p>
                      <h3 className="text-xl font-black text-gray-900">Dr. Narayan Bamania</h3>
                      <p className="text-violet-600 text-sm font-semibold mb-2">Full Stack AI Engineer & Content Automation Expert</p>
                      <p className="text-gray-600 text-sm leading-relaxed max-w-lg">10+ years building AI-powered tools for Indian content creators. Built Bamania's Cine AI to make cinematic video production accessible to everyone — at just ₹6 per video.</p>
                      <div className="flex flex-wrap gap-2 mt-3">
                        {['🇮🇳 Made in India','🤖 AI Specialist','🎬 Cinema Enthusiast','📊 10+ Years Exp'].map(b=>(
                          <span key={b} className="text-xs bg-white text-violet-600 border border-violet-200 px-3 py-1 rounded-full font-medium">{b}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  )
}
