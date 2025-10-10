import { createBrowserRouter } from "react-router";
import { Suspense, lazy } from "react";
import Layout from "../common/Layout";
import LoadingPage from "../common/LoadingPage";

const Home = lazy(() => import("../pages/HomePage"));
const Login = lazy(() => import("../pages/LoginPage"));
const Test = lazy(() => import("../pages/TestPage"));
const OAuthSuccess = lazy(() => import("../pages/OAuthSuccess"));
const MyPage = lazy(() => import("../pages/MyPage"));
const OAuthFail = lazy(() => import("../pages/OAuthFail"));
const TendencyGame = lazy(() => import("../pages/TendencyGamePage"));
const StockInfo = lazy(() => import("../pages/StockInfoPage"));
const Trade = lazy(() => import("../pages/TradePage"));
const TradeInfo = lazy(() => import("../pages/TradeInfoPage"));
const Search = lazy(() => import("../pages/SearchPage"));
const Influence = lazy(() => import("../pages/InfluencePage"));

const Router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />, // ✅
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<LoadingPage />}>
            <Home />
          </Suspense>
        ),
      },
      {
        path: "test",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <Test />
          </Suspense>
        ),
      },
      {
        path: "login",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <Login />
          </Suspense>
        ),
      },
      {
        path: "oauth/success",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <OAuthSuccess />
          </Suspense>
        ),
      },
      {
        path: "oauth/fail",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <OAuthFail />
          </Suspense>
        ),
      },
      {
        path: "mypage",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <MyPage />
          </Suspense>
        ),
      },
      {
        path: "search",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <Search />
          </Suspense>
        ),
      },
      {
        path: "game",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <TendencyGame />
          </Suspense>
        ),
      },

      {
        path: "trade",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <Trade />
          </Suspense>
        ),
      },
      {
        path: "trade/:ticker",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <TradeInfo />
          </Suspense>
        ),
      },
      {
        path: "stock/:ticker",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <StockInfo />
          </Suspense>
        ),
      },
      {
        path: "influence",
        element: (
          <Suspense fallback={<LoadingPage />}>
            <Influence />
          </Suspense>
        ),
      },
    ],
  },
]);

export default Router;
