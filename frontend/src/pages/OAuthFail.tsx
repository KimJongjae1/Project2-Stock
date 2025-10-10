import { useSearchParams, Link } from 'react-router';

export default function OAuthFail() {
  const [sp] = useSearchParams();
  return (
    <div className="min-h-dvh grid place-items-center bg-gray-50 p-6">
      <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-sm">
        <h2 className="mb-3 text-xl font-semibold">로그인에 실패했어요 😢</h2>
        <p className="text-gray-700">
          사유: <b>{sp.get('reason') ?? '알 수 없음'}</b>
        </p>

        <div className="mt-6">
          <Link
            to="/"
            className="inline-block rounded-lg bg-black px-4 py-2 text-white hover:opacity-90"
          >
            홈으로
          </Link>
        </div>
      </div>
    </div>
  );
}
