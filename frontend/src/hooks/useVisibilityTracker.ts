import { useEffect } from 'react';

const useVisibilityTracker = (onChange: (visible: boolean) => void) => {
  useEffect(() => {
    const handleVisibility = () => onChange(document.visibilityState === 'visible');
    const handleBlur = () => onChange(false);
    const handleFocus = () => onChange(true);

    document.addEventListener('visibilitychange', handleVisibility);
    window.addEventListener('blur', handleBlur);
    window.addEventListener('focus', handleFocus);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('blur', handleBlur);
      window.removeEventListener('focus', handleFocus);
    };
  }, [onChange]);
};

export default useVisibilityTracker;

