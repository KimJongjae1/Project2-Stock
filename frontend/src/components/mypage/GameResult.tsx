import type { MyPageData } from "../../types/MyPageData";
import { Link } from "react-router";

type Props = { data?: MyPageData["gameResult"] | null };
type PairKey = "I_E" | "S_N" | "F_T" | "P_J";

/** 타입별 닉네임/설명 */
const TYPE_META: Record<
  string,
  { nickname: string; pros?: string; cons?: string; tip?: string }
> = {
  ESTJ: {
    nickname: "쫄보",
    pros: "이슈에 흔들리지 않아서 변동성이 적음",
    cons: "과도한 신중함으로 매수/매도 기회를 놓칠 수 있음",
    tip: "장타 성향 유지 + 과도한 분석/신중함을 줄여 매수 타이밍을 빠르게",
  },
  ESTP: {
    nickname: "존버",
    pros: "정보와 뚝심을 겸비, 우량주 발굴해 장타로 수익",
    cons: "시장 급변 시 대처가 느릴 수 있음",
    tip: "현재 전략 유지, 정기 리밸런싱과 리스크 관리에 집중",
  },
  ESFJ: {
    nickname: "소심",
    pros: "자료 기반의 신중한 접근, 감정에 덜 휘둘림",
    cons: "비반응적이라 변동성 장에서 단기 이익 실현이 어려움",
    tip: "단타→장타 전환 또는 신중함을 활용해 승률/목표 수익률 상향",
  },
  ESFP: {
    nickname: "개고수",
    pros: "신중한 분석 기반 높은 타율의 단타로 고수익",
    cons: "지속 관찰 필요로 피로도 상승",
    tip: "현재 전략 정교화, 매매 기준 시스템화",
  },
  ENTJ: {
    nickname: "물타기",
    pros: "복잡한 분석 없이도 장기 보유를 고수",
    cons: "낮은 수익에도 과도한 장기 보유로 자금 묶임",
    tip: "장타 유지 + 매수 전 핵심 참고자료 체크 규칙 도입",
  },
  ENTP: {
    nickname: "마이웨이",
    pros: "혁신적 아이디어를 투자에 접목하는 능력이 뛰어남",
    cons: "정보 수집/분석 소홀로 악재에 취약",
    tip: "확신 기반 투자 유지 + 분기별 펀더멘털 점검으로 리스크 축소",
  },
  ENFJ: {
    nickname: "일단 고",
    pros: "진입/결정이 빠르고 손실에도 동요 적음",
    cons: "근거 부족 단타 반복으로 수익률 저조",
    tip: "장타 전환 또는 매수 전 최소 24시간 숙고",
  },
  ENFP: {
    nickname: "운용의 귀재",
    pros: "감정에 덜 흔들리고 기준 준수",
    cons: "감각 과신으로 큰 손실 위험",
    tip: "성공 매매를 지표화하여 데이터 기반으로 전환",
  },
  ISTJ: {
    nickname: "흑우",
    pros: "신중한 분석과 원칙적 태도",
    cons: "변동에 휘둘려 장기 이점 상실",
    tip: "비반응 훈련으로 매매 횟수 축소, 수익률 향상",
  },
  ISTP: {
    nickname: "기회주의자",
    pros: "신중한 분석으로 변동 활용 능력 우수",
    cons: "완벽한 기회만 기다리다 타이밍 놓칠 수 있음",
    tip: "과도한 단기 반응 자제, 장기 관점 유지",
  },
  ISFJ: {
    nickname: "주린이",
    pros: "신중한 자료 분석/상황 파악 능력",
    cons: "감정적 매매로 이어질 소지",
    tip: "손실 폭 엄격 관리 또는 우량주 장타로 전환",
  },
  ISFP: {
    nickname: "타이밍 장인",
    pros: "정보력 + 변동성 활용으로 단타 고수익",
    cons: "실패 시 손실 회복 집착 위험",
    tip: "매매 횟수 제한해 집중, 신중함 강화 및 피로도 관리",
  },
  INTJ: {
    nickname: "동학개미",
    pros: "기민한 행동력 + 장타 성향",
    cons: "비신중 상태에서 변동 반응으로 비합리적 매매 위험",
    tip: "변동 반응 기준 상향, 매매 횟수 대폭 축소",
  },
  INTP: {
    nickname: "몽상가",
    pros: "직관/반응 기반 장기 고수익 잠재력",
    cons: "비현실적 목표 고집",
    tip: "리스크 지표/손절 기준 마련해 엄격히 준수",
  },
  INFJ: {
    nickname: "한강",
    pros: "변동성 대응 결단력",
    cons: "충동 매매로 수익률 저조, 대손 위험",
    tip: "즉시 장타 전환 또는 최소 30분 숙고 규칙",
  },
  INFP: {
    nickname: "잭팟",
    pros: "감/반응으로 단타 잭팟 잠재력",
    cons: "성공 일반화로 과도한 위험 시도",
    tip: "고수익 후 원금 보호 출금 룰로 리스크 통제",
  },
};

export default function GameResult({ data }: Props) {
  if (!data) {
    return (
      <section className="w-full bg-slate-700 backdrop-blur-xl rounded-2xl shadow-lg p-6 border border-slate-600 relative">
        <div className="text-center space-y-4">
          <h2 className="text-2xl font-extrabold text-white mb-2">
            투자 성격 유형 진단 결과
          </h2>
          <div className="flex justify-center mb-4">
            <div className="w-16 h-16 rounded-full bg-slate-600 flex items-center justify-center">
              <svg
                width="32"
                height="32"
                viewBox="0 0 24 24"
                fill="none"
                className="text-slate-400"
              >
                <path
                  d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h2v2h-2v-2zm0-8h2v6h-2V9z"
                  fill="currentColor"
                />
              </svg>
            </div>
          </div>
          <p className="text-slate-400 mb-6">아직 진단을 받지 않으셨습니다.</p>
          <Link
            to="/game"
            className="px-6 py-3 bg-gradient-to-r from-amber-500 to-amber-600 text-white font-semibold rounded-lg hover:from-amber-600 hover:to-amber-700 transition-all shadow-lg"
          >
            성향 진단 시작하기
          </Link>
        </div>
      </section>
    );
  }

  const clamp = (n: number) => Math.max(0, Math.min(100, Math.round(n)));
  const labels = {
    I: "반응형",
    E: "마이웨이형",
    S: "신중형",
    N: "무심형",
    F: "단타형",
    T: "장타형",
    P: "재능형",
    J: "노력형",
  } as const;

  const rows: Array<{
    key: PairKey;
    leftCode: keyof typeof labels;
    rightCode: keyof typeof labels;
    leftPct: number;
    rightPct: number;
    gradient: string;
  }> = [
    {
      key: "I_E",
      leftCode: "I",
      rightCode: "E",
      leftPct: clamp(Number(data.tendencyI) || 0),
      rightPct: clamp(Number(data.tendencyE) || 0),
      gradient: "from-rose-400 to-rose-500",
    },
    {
      key: "S_N",
      leftCode: "S",
      rightCode: "N",
      leftPct: clamp(Number(data.tendencyS) || 0),
      rightPct: clamp(Number(data.tendencyN) || 0),
      gradient: "from-emerald-400 to-teal-500",
    },
    {
      key: "F_T",
      leftCode: "F",
      rightCode: "T",
      leftPct: clamp(Number(data.tendencyF) || 0),
      rightPct: clamp(Number(data.tendencyT) || 0),
      gradient: "from-lime-400 to-green-500",
    },
    {
      key: "P_J",
      leftCode: "P",
      rightCode: "J",
      leftPct: clamp(Number(data.tendencyP) || 0),
      rightPct: clamp(Number(data.tendencyJ) || 0),
      gradient: "from-pink-400 to-rose-400",
    },
  ];

  const typeTag = (data.tendencyResult || "").toUpperCase();
  const meta = TYPE_META[typeTag];

  return (
    <section className="w-full bg-slate-700 backdrop-blur-xl rounded-2xl shadow-lg p-6 border border-slate-600 relative">
      <div className="space-y-6">
        <header className="text-center">
          <h2 className="text-2xl font-extrabold text-white">
            투자 성격 유형 진단 결과
          </h2>
        </header>

        {/* ✅ 요약 카드 제거, 바로 상세 메타부터 */}
        {meta && (
          <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-600/60 space-y-2">
            <div className="text-white text-lg font-extrabold flex items-center gap-2">
              {meta.nickname}
              <span className="text-slate-300 text-sm">({typeTag})</span>
            </div>
            {meta.pros && (
              <div className="text-slate-200">
                <span className="text-emerald-300 font-semibold">장점</span> :{" "}
                {meta.pros}
              </div>
            )}
            {meta.cons && (
              <div className="text-slate-200">
                <span className="text-rose-300 font-semibold">단점</span> :{" "}
                {meta.cons}
              </div>
            )}
            {meta.tip && (
              <div className="text-slate-200">
                <span className="text-amber-300 font-semibold">추천</span> :{" "}
                {meta.tip}
              </div>
            )}
          </div>
        )}

        {/* 막대 차트 */}
        <div className="bg-slate-800/40 rounded-xl p-4 border border-slate-600/60">
          <ul className="space-y-5">
            {rows.map((r) => (
              <li key={r.key} className="space-y-2">
                <div className="flex justify-between text-xs text-slate-300">
                  <div className="flex items-center gap-2">
                    <span className="font-bold">{r.leftCode}</span>
                    <span className="opacity-80">{labels[r.leftCode]}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="opacity-80 text-right">
                      {labels[r.rightCode]}
                    </span>
                    <span className="font-bold">{r.rightCode}</span>
                  </div>
                </div>
                <div className="relative h-4 w-full bg-slate-200/20 rounded-full overflow-hidden">
                  <div
                    className={`absolute left-0 top-0 h-full bg-gradient-to-r ${r.gradient}`}
                    style={{ width: `${r.leftPct}%` }}
                  />
                </div>
                <div className="flex justify-between text-xs text-slate-300">
                  <span>{r.leftPct}%</span>
                  <span>{r.rightPct}%</span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* 마지막 진단 일자 */}
        <div className="flex justify-center">
          <div className="text-slate-400 text-sm flex items-center gap-2">
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              className="text-slate-400"
            >
              <path
                d="M7 2v2M17 2v2M4 8h16M5 12h14M5 16h10M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6Z"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span>
              마지막 진단 일자&nbsp;·&nbsp;{formatDateTime(data.createdAt)}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}

function formatDateTime(isoLike: string) {
  if (!isoLike) return "";
  try {
    const d = new Date(isoLike);
    const yyyy = d.getFullYear();
    const mm = String(d.getMonth() + 1).padStart(2, "0");
    const dd = String(d.getDate()).padStart(2, "0");
    const hh = String(d.getHours()).padStart(2, "0");
    const mi = String(d.getMinutes()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd} ${hh}:${mi}`;
  } catch {
    return isoLike;
  }
}
