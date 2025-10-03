import ChatDock from '@/components/ChatDock';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-dark font-sans">
      {/* Header */}
      <header className="relative backdrop-blur-md bg-glass-light border-b border-glass-medium">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <h1 className="text-3xl font-display font-bold text-white tracking-tight">
              Demo<span className="text-accent-neon">Bank</span>
            </h1>
            <div className="flex items-center space-x-4">
              <div className="text-white/80 font-medium">Welcome back!</div>
              <div className="w-10 h-10 rounded-xl bg-gradient-accent flex items-center justify-center">
                <span className="text-dark-950 font-bold text-lg">U</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-16 lg:py-24">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="relative backdrop-blur-xl bg-gradient-to-br from-emerald-900/40 via-teal-800/30 to-emerald-700/40 rounded-3xl shadow-glass-lg border border-glass-medium overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-br from-primary-900/20 to-secondary-900/20"></div>
            
            <div className="relative grid lg:grid-cols-2 gap-12 lg:gap-16 items-center p-8 lg:p-16">
              {/* Text Content */}
              <div className="text-center lg:text-left space-y-6">
                <h1 className="text-3xl md:text-4xl lg:text-5xl font-display font-bold text-white leading-tight tracking-tight">
                  Welcome to the{' '}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent-neon to-accent-400">
                    Future of Banking
                  </span>
                </h1>
                
                <p className="text-lg lg:text-xl text-white/80 leading-relaxed max-w-2xl mx-auto lg:mx-0">
                  Experience cutting-edge features, top-notch security, and instant access to your banking made better for you
                </p>
                
                <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start pt-4">
                  <button className="px-8 py-4 bg-gradient-accent text-dark-950 rounded-xl font-semibold hover:shadow-neon-lg transition-all duration-300 transform hover:scale-105">
                    Get Started
                  </button>
                  <button className="px-8 py-4 backdrop-blur-sm bg-glass-light border border-glass-medium text-white rounded-xl font-semibold hover:bg-glass-medium transition-all duration-300">
                    Learn More
                  </button>
                </div>
              </div>

              {/* Banking Cards */}
              <div className="relative flex justify-center items-center h-80 lg:h-96">
                {/* Card 1 - Green */}
                <div className="absolute transform rotate-12 translate-x-4 translate-y-2 hover:rotate-6 transition-transform duration-500">
                  <div className="w-72 h-44 bg-gradient-primary rounded-2xl shadow-2xl border border-white/20 p-6 backdrop-blur-sm">
                    <div className="flex justify-between items-start mb-8">
                      <div className="text-white">
                        <p className="text-sm font-medium opacity-80">DemoBank Card</p>
                        <p className="text-xs opacity-60">Premium</p>
                      </div>
                      <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                        <div className="w-4 h-4 bg-white rounded-full"></div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <p className="text-white font-mono text-lg tracking-wider">•••• •••• •••• 4567</p>
                      <div className="flex justify-between">
                        <div>
                          <p className="text-white/60 text-xs">Valid Thru</p>
                          <p className="text-white text-sm font-medium">12/28</p>
                        </div>
                        <div className="text-right">
                          <p className="text-white/60 text-xs">CVV</p>
                          <p className="text-white text-sm font-medium">•••</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Card 2 - Yellow/Gold */}
                <div className="absolute transform -rotate-6 -translate-x-4 -translate-y-2 hover:rotate-0 transition-transform duration-500">
                  <div className="w-72 h-44 bg-gradient-to-br from-yellow-400 via-yellow-500 to-yellow-600 rounded-2xl shadow-2xl border border-yellow-300/30 p-6">
                    <div className="flex justify-between items-start mb-8">
                      <div className="text-dark-950">
                        <p className="text-sm font-medium">DemoBank Gold</p>
                        <p className="text-xs opacity-70">Elite</p>
                      </div>
                      <div className="w-8 h-8 bg-dark-950/20 rounded-full flex items-center justify-center">
                        <div className="w-4 h-4 bg-dark-950 rounded-full"></div>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <p className="text-dark-950 font-mono text-lg tracking-wider">•••• •••• •••• 8901</p>
                      <div className="flex justify-between">
                        <div>
                          <p className="text-dark-950/60 text-xs">Valid Thru</p>
                          <p className="text-dark-950 text-sm font-medium">09/27</p>
                        </div>
                        <div className="text-right">
                          <p className="text-dark-950/60 text-xs">CVV</p>
                          <p className="text-dark-950 text-sm font-medium">•••</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Decorative Elements */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-accent-neon/10 rounded-full blur-3xl"></div>
            <div className="absolute bottom-0 left-0 w-48 h-48 bg-secondary-500/10 rounded-full blur-3xl"></div>
          </div>
        </div>
      </section>

      {/* Main Dashboard */}
      <main className="max-w-7xl mx-auto px-6 lg:px-8 py-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
          {/* Balance Card */}
          <div className="relative backdrop-blur-lg bg-gradient-primary rounded-2xl shadow-glass p-8 border border-glass-light group hover:shadow-glass-lg transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-white/80 mb-2">Total Balance</p>
                <p className="text-4xl font-bold text-white tracking-tight">$12,345.67</p>
              </div>
              <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-white/20">
              <span className="text-sm text-accent-neon font-semibold">+2.5%</span>
              <span className="text-sm text-white/70 ml-2">from last month</span>
            </div>
          </div>

          {/* Cards Card */}
          <div className="relative backdrop-blur-lg bg-gradient-secondary rounded-2xl shadow-glass p-8 border border-glass-light group hover:shadow-glass-lg transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-white/80 mb-2">Active Cards</p>
                <p className="text-4xl font-bold text-white tracking-tight">3</p>
              </div>
              <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-white/20 space-y-1">
              <div className="text-sm text-white/80">Visa •••• 4567</div>
              <div className="text-sm text-white/80">MasterCard •••• 8901</div>
            </div>
          </div>

          {/* Insights Card */}
          <div className="relative backdrop-blur-lg bg-gradient-accent rounded-2xl shadow-glass p-8 border border-glass-light group hover:shadow-glass-lg transition-all duration-300">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-dark-950/80 mb-2">Monthly Spending</p>
                <p className="text-4xl font-bold text-dark-950 tracking-tight">$2,890</p>
              </div>
              <div className="w-16 h-16 bg-dark-950/20 rounded-2xl flex items-center justify-center backdrop-blur-sm">
                <svg className="w-8 h-8 text-dark-950" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
            </div>
            <div className="mt-6 pt-4 border-t border-dark-950/20">
              <span className="text-sm text-primary-700 font-semibold">+15%</span>
              <span className="text-sm text-dark-950/70 ml-2">vs last month</span>
            </div>
          </div>
        </div>

        {/* Recent Transactions */}
        <div className="relative backdrop-blur-lg bg-glass-light rounded-2xl shadow-glass p-8 border border-glass-medium mb-10">
          <h2 className="text-2xl font-display font-bold text-white mb-6">Recent Transactions</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-4 rounded-xl bg-glass-dark backdrop-blur-sm hover:bg-glass-medium transition-all duration-200">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-red-500/20 rounded-xl flex items-center justify-center mr-4">
                  <span className="text-red-400 font-bold text-lg">A</span>
                </div>
                <div>
                  <p className="font-semibold text-white">Amazon Purchase</p>
                  <p className="text-sm text-white/60">Yesterday</p>
                </div>
              </div>
              <span className="font-bold text-red-400 text-lg">-$89.99</span>
            </div>
            <div className="flex justify-between items-center p-4 rounded-xl bg-glass-dark backdrop-blur-sm hover:bg-glass-medium transition-all duration-200">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-primary-500/20 rounded-xl flex items-center justify-center mr-4">
                  <span className="text-primary-400 font-bold text-lg">S</span>
                </div>
                <div>
                  <p className="font-semibold text-white">Salary Deposit</p>
                  <p className="text-sm text-white/60">3 days ago</p>
                </div>
              </div>
              <span className="font-bold text-primary-400 text-lg">+$3,500.00</span>
            </div>
            <div className="flex justify-between items-center p-4 rounded-xl bg-glass-dark backdrop-blur-sm hover:bg-glass-medium transition-all duration-200">
              <div className="flex items-center">
                <div className="w-12 h-12 bg-orange-500/20 rounded-xl flex items-center justify-center mr-4">
                  <span className="text-orange-400 font-bold text-lg">G</span>
                </div>
                <div>
                  <p className="font-semibold text-white">Grocery Store</p>
                  <p className="text-sm text-white/60">5 days ago</p>
                </div>
              </div>
              <span className="font-bold text-red-400 text-lg">-$127.45</span>
            </div>
          </div>
        </div>

        {/* Floating ChatDock Component */}
        <ChatDock />
      </main>
    </div>
  );
}
