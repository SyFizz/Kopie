/**
 * AuthContext — gestion de la session enseignant côté front (Story 1.4).
 *
 * Conformément à `architecture.md#Authentication & Security` :
 * - L'access token JWT est conservé EN MÉMOIRE uniquement (jamais
 *   localStorage / sessionStorage — protection XSS).
 * - Le refresh token vit dans un cookie `httpOnly Secure SameSite=Strict`
 *   posé par l'API ; le navigateur l'envoie automatiquement à
 *   `POST /api/v1/auth/refresh` sous réserve que `credentials: 'include'`
 *   soit positionné sur le fetch.
 * - La déconnexion `logout()` est tolérante aux erreurs réseau : on efface
 *   toujours l'état local même si l'API n'a pas pu être jointe.
 */
import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { logoutTeacher } from './api'

export interface AuthContextValue {
  /** Access token JWT en mémoire (ou null si non connecté). */
  accessToken: string | null
  /** Permet d'écrire/effacer l'access token (utilisé par LoginPage / logout). */
  setAccessToken: (token: string | null) => void
  /**
   * Déconnecte l'utilisateur : appelle l'API pour supprimer le cookie
   * refresh puis efface l'access token en mémoire. Tolère un échec
   * d'appel réseau (l'état local est toujours nettoyé).
   */
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export interface AuthProviderProps {
  children: ReactNode
  /**
   * Permet de pré-positionner l'access token au montage (utilisé par les
   * tests pour court-circuiter le flux login + par la future rehydratation
   * silencieuse de la story 1.5 qui appellera `/auth/refresh` au démarrage).
   */
  initialAccessToken?: string | null
}

export function AuthProvider({
  children,
  initialAccessToken = null,
}: AuthProviderProps) {
  const [accessToken, setAccessTokenState] = useState<string | null>(
    initialAccessToken,
  )

  const setAccessToken = useCallback((token: string | null) => {
    setAccessTokenState(token)
  }, [])

  const logout = useCallback(async () => {
    try {
      await logoutTeacher()
    } finally {
      setAccessTokenState(null)
    }
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({ accessToken, setAccessToken, logout }),
    [accessToken, setAccessToken, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

// Co-localiser hook et provider est volontaire (un seul point d'entrée
// pour le contexte) ; on accepte la perte du react-refresh sur ce fichier.
// eslint-disable-next-line react-refresh/only-export-components
export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (ctx === null) {
    throw new Error('useAuth doit être utilisé à l\'intérieur d\'un <AuthProvider>')
  }
  return ctx
}
