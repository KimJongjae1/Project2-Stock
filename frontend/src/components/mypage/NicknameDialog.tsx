import React, { useEffect, useState } from 'react';
import { api } from '../../api/client';

type Props = {
  open: boolean;
  initialNickname?: string;
  onClose: () => void;
  onSaved: (newNickname: string) => void;
};

type UserSummary = { nickname: string; [k: string]: unknown };
type ApiError = { response?: { data?: { message?: string; error?: string } } };
const extractMsg = (err: unknown) => {
  if (typeof err === 'object' && err !== null) {
    const e = err as ApiError;
    return e.response?.data?.message ?? e.response?.data?.error;
  }
  return undefined;
};

const NicknameDialog: React.FC<Props> = ({ open, initialNickname, onClose, onSaved }) => {
  const [nick, setNick] = useState(initialNickname ?? '');
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    setNick(initialNickname ?? '');
    setError(null);
  }, [open, initialNickname]);

  const validateFormat = (v: string) => {
    if (!v || v.trim().length < 2) return '닉네임은 2자 이상이어야 해요.';
    if (v.length > 30) return '닉네임은 최대 30자까지 가능합니다.';
    if (!/^[\w가-힣\- ]+$/.test(v)) return '한글/영문/숫자/_/-/공백만 사용할 수 있어요.';
    return null;
  };

  useEffect(() => {
    if (!open) return;
    if (!nick) {
      setError(null);
      return;
    }
    setError(validateFormat(nick));
  }, [nick, open]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const fmtErr = validateFormat(nick);
    if (fmtErr) return setError(fmtErr);

    try {
      setSaving(true);
      const body = { nickname: nick.trim() };
      const res = await api.patch<UserSummary>('/api/users/me', body);
      onSaved(res.nickname ?? body.nickname);
      onClose();
    } catch (err: unknown) {
      const msg = extractMsg(err) ?? '닉네임 저장에 실패했어요.';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  if (!open) return null;

  const canSubmit = !saving && !error && nick.trim().length >= 2 && nick.trim().length <= 30;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm grid place-items-center z-50">
      <form
        onSubmit={onSubmit}
        className="w-[420px] rounded-2xl bg-slate-700 p-6 shadow-2xl border border-slate-600"
      >
        <h2 className="text-xl font-bold mb-3 text-white">닉네임 설정</h2>
        <p className="text-sm text-slate-300 mb-4">서비스에서 사용할 닉네임을 정해주세요.</p>

        <input
          autoFocus
          value={nick}
          onChange={(e) => setNick(e.target.value)}
          className="w-full border border-slate-500 bg-slate-600 text-white rounded-lg px-3 py-2 mb-2 focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400 placeholder-slate-400"
          placeholder="예) 테토보이즈리더"
        />

        {!error && nick && (
          <div className="text-sm text-amber-400 mb-2 flex items-center gap-1">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
              />
            </svg>
            사용 가능한 닉네임입니다.
          </div>
        )}
        {error && (
          <div className="text-sm text-red-400 mb-2 flex items-center gap-1">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                stroke="currentColor"
                strokeWidth="2"
                fill="none"
              />
            </svg>
            {error}
          </div>
        )}

        <div className="flex justify-end gap-2 mt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 rounded-lg border border-slate-500 bg-slate-600 text-slate-200 hover:bg-slate-500 transition-all"
          >
            취소
          </button>
          <button
            type="submit"
            disabled={!canSubmit}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-amber-500 to-amber-600 text-white hover:from-amber-600 hover:to-amber-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            {saving ? '저장 중…' : '저장'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default NicknameDialog;
