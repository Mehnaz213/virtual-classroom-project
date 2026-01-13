import { Navigate, Route, Routes, BrowserRouter } from 'react-router-dom';

import { AuthProvider, useAuth } from './context/AuthContext';
import LabelingPage from './pages/LabelingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import StudentJoin from './pages/StudentJoin';
import LabelerPage from './pages/LabelerPage';
import TeacherDashboard from './pages/TeacherDashboard';

type ProtectedProps = {
  children: JSX.Element;
  requiredRole?: 'teacher' | 'student';
};

const ProtectedRoute = ({ children, requiredRole }: ProtectedProps) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/" replace />;
  }
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to={`/${user.role}`} replace />;
  }
  return children;
};

const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<LoginPage />} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route
      path="/teacher"
      element={
        <ProtectedRoute requiredRole="teacher">
          <TeacherDashboard />
        </ProtectedRoute>
      }
    />
    <Route
      path="/student"
      element={
        <ProtectedRoute requiredRole="student">
          <StudentJoin />
        </ProtectedRoute>
      }
    />
    <Route
      path="/labeler"
      element={
        <ProtectedRoute requiredRole="teacher">
          <LabelerPage />
        </ProtectedRoute>
      }
    />
    <Route
      path="/labeler"
      element={
        <ProtectedRoute requiredRole="teacher">
          <LabelingPage />
        </ProtectedRoute>
      }
    />
    <Route path="*" element={<Navigate to="/" replace />} />
  </Routes>
);

const App = () => (
  <AuthProvider>
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  </AuthProvider>
);

export default App;

