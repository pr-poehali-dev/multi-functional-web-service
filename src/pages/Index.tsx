import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import Icon from '@/components/ui/icon';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';

const translations = {
  ru: {
    title: 'Многофункциональный Веб-Сервис',
    subtitle: 'Ваше личное пространство для контента, файлов и развлечений',
    login: 'Вход',
    register: 'Регистрация',
    email: 'Электронная почта',
    password: 'Пароль',
    confirmPassword: 'Подтвердите пароль',
    signIn: 'Войти',
    signUp: 'Зарегистрироваться',
    dashboard: 'Панель управления',
    profile: 'Профиль',
    streaming: 'Стриминг',
    games: 'Игры',
    files: 'Файлы',
    settings: 'Настройки',
    darkMode: 'Темная тема',
    language: 'Язык',
    streamingPlatforms: 'Стриминговые платформы',
    gameLibrary: 'Игровая библиотека',
    fileManager: 'Файловый менеджер',
    addPlatform: 'Добавить платформу',
    addGame: 'Добавить игру',
    uploadFile: 'Загрузить файл',
    privacy: 'Конфиденциальность',
    security: '2FA Безопасность',
    logout: 'Выйти',
    welcomeBack: 'С возвращением!',
    recentFiles: 'Недавние файлы',
    popularGames: 'Популярные игры',
    myPlatforms: 'Мои платформы',
  },
  en: {
    title: 'Multifunctional Web Service',
    subtitle: 'Your personal space for content, files and entertainment',
    login: 'Login',
    register: 'Register',
    email: 'Email',
    password: 'Password',
    confirmPassword: 'Confirm Password',
    signIn: 'Sign In',
    signUp: 'Sign Up',
    dashboard: 'Dashboard',
    profile: 'Profile',
    streaming: 'Streaming',
    games: 'Games',
    files: 'Files',
    settings: 'Settings',
    darkMode: 'Dark Mode',
    language: 'Language',
    streamingPlatforms: 'Streaming Platforms',
    gameLibrary: 'Game Library',
    fileManager: 'File Manager',
    addPlatform: 'Add Platform',
    addGame: 'Add Game',
    uploadFile: 'Upload File',
    privacy: 'Privacy',
    security: '2FA Security',
    logout: 'Logout',
    welcomeBack: 'Welcome Back!',
    recentFiles: 'Recent Files',
    popularGames: 'Popular Games',
    myPlatforms: 'My Platforms',
  },
};

type Language = 'ru' | 'en';

const Index = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isDark, setIsDark] = useState(false);
  const [language, setLanguage] = useState<Language>('ru');
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showAddDialog, setShowAddDialog] = useState(false);
  const [dialogType, setDialogType] = useState<'platform' | 'game' | 'file'>('platform');

  const t = translations[language];

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  const toggleLanguage = () => {
    setLanguage(language === 'ru' ? 'en' : 'ru');
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuthenticated(true);
    toast.success(language === 'ru' ? 'Успешный вход!' : 'Login successful!');
  };

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuthenticated(true);
    toast.success(language === 'ru' ? 'Регистрация завершена!' : 'Registration complete!');
  };

  const openAddDialog = (type: 'platform' | 'game' | 'file') => {
    setDialogType(type);
    setShowAddDialog(true);
  };

  const streamingPlatforms = [
    { name: 'Netflix', icon: 'Tv', color: 'bg-red-500' },
    { name: 'YouTube', icon: 'Play', color: 'bg-red-600' },
    { name: 'Twitch', icon: 'Radio', color: 'bg-purple-500' },
    { name: 'Spotify', icon: 'Music', color: 'bg-green-500' },
  ];

  const games = [
    { name: 'Cyberpunk 2077', hours: 45, status: 'playing' },
    { name: 'The Witcher 3', hours: 120, status: 'completed' },
    { name: 'Red Dead Redemption 2', hours: 32, status: 'playing' },
    { name: 'Baldur\'s Gate 3', hours: 78, status: 'playing' },
  ];

  const files = [
    { name: 'Project_Docs.pdf', size: '2.3 MB', type: 'document' },
    { name: 'Vacation_Photos.zip', size: '145 MB', type: 'archive' },
    { name: 'Presentation.pptx', size: '5.7 MB', type: 'document' },
  ];

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5 flex items-center justify-center p-4">
        <div className="absolute top-4 right-4 flex gap-2">
          <Button variant="outline" size="sm" onClick={toggleLanguage}>
            <Icon name="Languages" className="mr-2 h-4 w-4" />
            {language.toUpperCase()}
          </Button>
          <Button variant="outline" size="sm" onClick={toggleTheme}>
            <Icon name={isDark ? 'Sun' : 'Moon'} className="h-4 w-4" />
          </Button>
        </div>

        <Card className="w-full max-w-4xl p-8 backdrop-blur-sm bg-card/95 border-2 animate-scale-in">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center mb-4">
              <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Icon name="Rocket" className="h-8 w-8 text-white" />
              </div>
            </div>
            <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
              {t.title}
            </h1>
            <p className="text-muted-foreground">{t.subtitle}</p>
          </div>

          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2 mb-6">
              <TabsTrigger value="login">{t.login}</TabsTrigger>
              <TabsTrigger value="register">{t.register}</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <Label htmlFor="login-email">{t.email}</Label>
                  <Input id="login-email" type="email" placeholder="user@example.com" required />
                </div>
                <div>
                  <Label htmlFor="login-password">{t.password}</Label>
                  <Input id="login-password" type="password" required />
                </div>
                <Button type="submit" className="w-full" size="lg">
                  <Icon name="LogIn" className="mr-2 h-4 w-4" />
                  {t.signIn}
                </Button>
              </form>
            </TabsContent>

            <TabsContent value="register">
              <form onSubmit={handleRegister} className="space-y-4">
                <div>
                  <Label htmlFor="register-email">{t.email}</Label>
                  <Input id="register-email" type="email" placeholder="user@example.com" required />
                </div>
                <div>
                  <Label htmlFor="register-password">{t.password}</Label>
                  <Input id="register-password" type="password" required />
                </div>
                <div>
                  <Label htmlFor="confirm-password">{t.confirmPassword}</Label>
                  <Input id="confirm-password" type="password" required />
                </div>
                <Button type="submit" className="w-full" size="lg">
                  <Icon name="UserPlus" className="mr-2 h-4 w-4" />
                  {t.signUp}
                </Button>
              </form>
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-primary/5">
      <nav className="border-b bg-card/50 backdrop-blur-md sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Icon name="Rocket" className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl">{t.title.split(' ')[0]}</span>
          </div>

          <div className="flex items-center gap-2">
            <Button variant="ghost" size="sm" onClick={toggleLanguage}>
              <Icon name="Languages" className="mr-2 h-4 w-4" />
              {language.toUpperCase()}
            </Button>
            <Button variant="ghost" size="sm" onClick={toggleTheme}>
              <Icon name={isDark ? 'Sun' : 'Moon'} className="h-4 w-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => setIsAuthenticated(false)}>
              <Icon name="LogOut" className="mr-2 h-4 w-4" />
              {t.logout}
            </Button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-6">
        <div className="grid lg:grid-cols-[240px_1fr] gap-6">
          <aside className="space-y-2">
            <Card className="p-2">
              <Button
                variant={activeTab === 'dashboard' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveTab('dashboard')}
              >
                <Icon name="LayoutDashboard" className="mr-2 h-4 w-4" />
                {t.dashboard}
              </Button>
              <Button
                variant={activeTab === 'profile' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveTab('profile')}
              >
                <Icon name="User" className="mr-2 h-4 w-4" />
                {t.profile}
              </Button>
              <Button
                variant={activeTab === 'streaming' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveTab('streaming')}
              >
                <Icon name="Tv" className="mr-2 h-4 w-4" />
                {t.streaming}
              </Button>
              <Button
                variant={activeTab === 'games' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveTab('games')}
              >
                <Icon name="Gamepad2" className="mr-2 h-4 w-4" />
                {t.games}
              </Button>
              <Button
                variant={activeTab === 'files' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveTab('files')}
              >
                <Icon name="FolderOpen" className="mr-2 h-4 w-4" />
                {t.files}
              </Button>
              <Button
                variant={activeTab === 'settings' ? 'default' : 'ghost'}
                className="w-full justify-start"
                onClick={() => setActiveTab('settings')}
              >
                <Icon name="Settings" className="mr-2 h-4 w-4" />
                {t.settings}
              </Button>
            </Card>
          </aside>

          <main className="animate-fade-in">
            {activeTab === 'dashboard' && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-3xl font-bold mb-2">{t.welcomeBack}</h2>
                  <p className="text-muted-foreground">user@example.com</p>
                </div>

                <div className="grid md:grid-cols-3 gap-4">
                  <Card className="p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-xl bg-primary/10 flex items-center justify-center">
                        <Icon name="Tv" className="h-6 w-6 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">{t.myPlatforms}</p>
                        <p className="text-2xl font-bold">{streamingPlatforms.length}</p>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-xl bg-secondary/10 flex items-center justify-center">
                        <Icon name="Gamepad2" className="h-6 w-6 text-secondary" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">{t.popularGames}</p>
                        <p className="text-2xl font-bold">{games.length}</p>
                      </div>
                    </div>
                  </Card>

                  <Card className="p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-xl bg-accent/10 flex items-center justify-center">
                        <Icon name="FolderOpen" className="h-6 w-6 text-accent" />
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">{t.recentFiles}</p>
                        <p className="text-2xl font-bold">{files.length}</p>
                      </div>
                    </div>
                  </Card>
                </div>

                <Card className="p-6">
                  <h3 className="text-xl font-semibold mb-4">{t.recentFiles}</h3>
                  <div className="space-y-2">
                    {files.map((file, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 rounded-lg hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                            <Icon name="FileText" className="h-5 w-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-medium">{file.name}</p>
                            <p className="text-sm text-muted-foreground">{file.size}</p>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm">
                          <Icon name="Download" className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            )}

            {activeTab === 'streaming' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-3xl font-bold">{t.streamingPlatforms}</h2>
                  <Button onClick={() => openAddDialog('platform')}>
                    <Icon name="Plus" className="mr-2 h-4 w-4" />
                    {t.addPlatform}
                  </Button>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {streamingPlatforms.map((platform, idx) => (
                    <Card key={idx} className="p-6 hover:shadow-lg transition-all hover:scale-105">
                      <div className="flex items-center gap-4">
                        <div className={`h-14 w-14 rounded-2xl ${platform.color} flex items-center justify-center`}>
                          <Icon name={platform.icon as any} className="h-7 w-7 text-white" />
                        </div>
                        <div>
                          <p className="font-semibold text-lg">{platform.name}</p>
                          <Badge variant="secondary">Active</Badge>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'games' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-3xl font-bold">{t.gameLibrary}</h2>
                  <Button onClick={() => openAddDialog('game')}>
                    <Icon name="Plus" className="mr-2 h-4 w-4" />
                    {t.addGame}
                  </Button>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  {games.map((game, idx) => (
                    <Card key={idx} className="p-6 hover:shadow-lg transition-shadow">
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="font-semibold text-lg mb-1">{game.name}</h3>
                          <p className="text-sm text-muted-foreground">{game.hours} {language === 'ru' ? 'часов' : 'hours'}</p>
                        </div>
                        <Badge variant={game.status === 'completed' ? 'default' : 'secondary'}>
                          {game.status === 'playing' ? (language === 'ru' ? 'Играю' : 'Playing') : (language === 'ru' ? 'Пройдено' : 'Completed')}
                        </Badge>
                      </div>
                      <div className="flex gap-2">
                        <Button variant="outline" size="sm" className="flex-1">
                          <Icon name="Play" className="mr-2 h-4 w-4" />
                          {language === 'ru' ? 'Запустить' : 'Launch'}
                        </Button>
                        <Button variant="outline" size="sm">
                          <Icon name="MoreVertical" className="h-4 w-4" />
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'files' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-3xl font-bold">{t.fileManager}</h2>
                  <Button onClick={() => openAddDialog('file')}>
                    <Icon name="Upload" className="mr-2 h-4 w-4" />
                    {t.uploadFile}
                  </Button>
                </div>

                <Card className="p-8 border-dashed border-2 hover:border-primary transition-colors">
                  <div className="text-center">
                    <div className="h-16 w-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
                      <Icon name="Upload" className="h-8 w-8 text-primary" />
                    </div>
                    <h3 className="font-semibold mb-2">{language === 'ru' ? 'Загрузите файлы' : 'Upload Files'}</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      {language === 'ru' ? 'Перетащите файлы сюда или нажмите для выбора' : 'Drag and drop files here or click to select'}
                    </p>
                    <Button>{language === 'ru' ? 'Выбрать файлы' : 'Select Files'}</Button>
                  </div>
                </Card>

                <div className="space-y-2">
                  {files.map((file, idx) => (
                    <Card key={idx} className="p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="h-12 w-12 rounded-lg bg-secondary/10 flex items-center justify-center">
                            <Icon name="FileText" className="h-6 w-6 text-secondary" />
                          </div>
                          <div>
                            <p className="font-medium">{file.name}</p>
                            <p className="text-sm text-muted-foreground">{file.size}</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="sm">
                            <Icon name="Eye" className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Icon name="Download" className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Icon name="Trash2" className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <h2 className="text-3xl font-bold">{t.settings}</h2>

                <Card className="p-6">
                  <h3 className="text-xl font-semibold mb-4">{t.privacy}</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{language === 'ru' ? 'Сбор аналитики' : 'Analytics Collection'}</p>
                        <p className="text-sm text-muted-foreground">
                          {language === 'ru' ? 'Разрешить сбор данных для улучшения сервиса' : 'Allow data collection to improve service'}
                        </p>
                      </div>
                      <Switch />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{language === 'ru' ? 'Логирование действий' : 'Action Logging'}</p>
                        <p className="text-sm text-muted-foreground">
                          {language === 'ru' ? 'Записывать пользовательские действия' : 'Record user actions'}
                        </p>
                      </div>
                      <Switch />
                    </div>
                  </div>
                </Card>

                <Card className="p-6">
                  <h3 className="text-xl font-semibold mb-4">{t.security}</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{language === 'ru' ? 'Двухфакторная аутентификация' : 'Two-Factor Authentication'}</p>
                        <p className="text-sm text-muted-foreground">
                          {language === 'ru' ? 'Дополнительная защита вашего аккаунта' : 'Extra protection for your account'}
                        </p>
                      </div>
                      <Switch />
                    </div>
                    <Button variant="outline" className="w-full">
                      <Icon name="Key" className="mr-2 h-4 w-4" />
                      {language === 'ru' ? 'Настроить 2FA' : 'Configure 2FA'}
                    </Button>
                  </div>
                </Card>

                <Card className="p-6 border-destructive">
                  <h3 className="text-xl font-semibold mb-4 text-destructive">
                    {language === 'ru' ? 'Опасная зона' : 'Danger Zone'}
                  </h3>
                  <Button variant="destructive" className="w-full">
                    <Icon name="Trash2" className="mr-2 h-4 w-4" />
                    {language === 'ru' ? 'Удалить аккаунт' : 'Delete Account'}
                  </Button>
                </Card>
              </div>
            )}
          </main>
        </div>
      </div>

      <Dialog open={showAddDialog} onOpenChange={setShowAddDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {dialogType === 'platform' && t.addPlatform}
              {dialogType === 'game' && t.addGame}
              {dialogType === 'file' && t.uploadFile}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label>{language === 'ru' ? 'Название' : 'Name'}</Label>
              <Input placeholder={language === 'ru' ? 'Введите название' : 'Enter name'} />
            </div>
            <Button className="w-full" onClick={() => {
              toast.success(language === 'ru' ? 'Успешно добавлено!' : 'Successfully added!');
              setShowAddDialog(false);
            }}>
              {language === 'ru' ? 'Добавить' : 'Add'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Index;
