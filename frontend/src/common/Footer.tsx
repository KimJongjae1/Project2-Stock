export default function Footer() {
  return (
    <footer className="bg-slate-800 text-white mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 lg:py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          {/* 서비스 소개 */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-amber-400 to-amber-600 rounded-lg flex items-center justify-center">
                <span className="text-slate-900 font-bold text-sm sm:text-base">
                  ₩
                </span>
              </div>
              <h3 className="text-lg sm:text-xl lg:text-2xl font-bold">
                TetoBoys
              </h3>
            </div>
            <p className="text-slate-300 mb-3 sm:mb-4 leading-relaxed text-sm sm:text-base">
              안전하고 재미있는 모의 투자 게임으로 투자 실력을 키워보세요.
            </p>
            <p className="text-slate-300 mb-4 leading-relaxed text-sm sm:text-base">
              실제 주식 데이터를 기반으로 한 리얼한 투자 경험을 제공합니다.
            </p>
          </div>

          {/* 팀 정보 메뉴 */}
          <div>
            <h4 className="font-semibold text-white mb-3 sm:mb-4 text-base sm:text-lg">
              팀 정보
            </h4>
            <ul className="space-y-2 sm:space-y-3 text-slate-300 text-sm sm:text-base">
              <li>
                <p className="transition-colors">
                  <span className="font-medium text-amber-400">팀명:</span>{" "}
                  테토보이즈
                </p>
              </li>
              <li>
                <p className="transition-colors">
                  <span className="font-medium text-amber-400">팀장:</span>{" "}
                  김종재
                </p>
              </li>
              <li>
                <p className="transition-colors">
                  <span className="font-medium text-amber-400">팀원:</span>{" "}
                  지성현, 이상용, 김대정, 장동현, 정연수
                </p>
              </li>
            </ul>
          </div>
        </div>

        {/* 투자 경고 문구 */}
        <div className="mt-6 sm:mt-8 p-3 sm:p-4 bg-slate-700 rounded-lg border-l-4 border-amber-500">
          <div className="flex flex-col sm:flex-row sm:items-start gap-2 sm:gap-3">
            <div className="text-amber-400 text-lg sm:text-xl flex-shrink-0">
              ⚠️
            </div>
            <div className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              <span className="font-medium text-amber-400">투자 유의사항:</span>
              <br className="sm:hidden" />
              <span className="sm:ml-1">
                본 서비스는 모의 투자 게임으로, 실제 투자와는 다를 수 있습니다.
                실제 투자 시에는 원금 손실 위험이 있으니 신중하게 결정하시기
                바랍니다.
              </span>
            </div>
          </div>
        </div>

        {/* 저작권 정보 */}
        <div className="mt-6 sm:mt-8 pt-4 sm:pt-6 border-t border-slate-600">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-3 text-xs sm:text-sm text-slate-400">
            <p>© 2024 TetoBoys. All rights reserved.</p>
            <p className="text-center sm:text-right">
              Educational purposes only • Not for commercial use
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
}
