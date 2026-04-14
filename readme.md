## 2026.3.21_10:10 创建

### 1.

使用Vue构建一个基本包

Frontend
```Bash
npm install

npm run dev
```

Backend
```Bash
pip install -r requirements.txt

uvicorn executed:app --host 0.0.0.0 --port 8326 --reload
```

围绕三个核心控制点：对话框、侧边栏和开始提示语

对话框负责完整聊天交互，包括messageList渲染、输入发送、自动滚动loading与错误处理，本质是围绕信息流的持续追加更新。

侧边栏用于管理多会话，维护conversationList和activeConversationId，支持新建、切换、删除、会话切换时驱动对话内容整体替换。

开始提示语在messageList为空时显示，用于引导用户开始提问，收条消息自动消失，并可通过示例直接触发对话。

### 2. 

相关的函数和参数
见注释

核心数据结构
核心数据结构可以理解为：整个chatBot前端其实就是在管理“会话集合，当前会话，当前会话里的消息集合”这三层关系。其中最外层是conversationList,表示系统里独有的对话会话；中间层是activeConversationId，表示用户当前正在查看哪一个对话；最内层是messageList，表示某个具体的会话里面已经发生过的消息流。这样拆开之后，多会话、切换上下文、保留历史记录这些功能都能自然成立。

conversationList: Conversation[]：会话集合
是整个应用最核心的状态容器，它保存的是“所有会话”的数组。数组里的每一项都是一个Conversation对象，所以他不是单纯标题列表，而是完整的会话激励集合。之所以用数组，是因为侧边栏本质上就是按顺序展示多个会话；之所以每个会话都独立保存自己的数据，是为了让用户切换会话时，右侧聊天区可以直接整体替换成该会话对应的内容，而不是重新计算或混在一起。


Conversation = { id, title, messageList, createdAt, updatedAt }
表示“单个会话”的完整数据单元。id 是唯一标识，用来做查找、切换、删除和高亮判断，前端里它的作用相当于这条会话的身份证；title 是侧边栏展示给用户看的会话名称，可能是默认生成的“新对话 1”，也可能是根据首条消息自动提炼出来的摘要；messageList 是这个会话内部的消息数组，真正的聊天内容都放在这里；createdAt 表示会话创建时间，方便以后做排序、展示或持久化；updatedAt 表示最近一次变动时间，通常在新增消息后更新，它最适合用来控制“最近活跃会话排序”。


messageList: Message[]：消息列表
是某一个会话内部的消息流，不是全局共享的，而是严格挂在某个Converstaion下面。这样设计的意义在于：用户切换会话时，本质上只是把当前渲染目标从A会话的messageList，换成B会话的messageList。因此对话框组建不需要知道所有会话，它只要拿到当前会话的messageList就能正常显示。这种设计让组建职责职责更清晰，也避免不同会话的消息互相污染。


Message = { id, role: 'user' | 'assistant', content, status?, time }
表示一条最小聊天消息。id 用来保证每条消息在列表渲染时可唯一识别，避免更新混乱；role 用来区分消息是谁发的，通常决定它显示在左边还是右边，也决定不同样式；content 是消息正文，是对话框真正渲染的文本内容；status 是可选字段，一般用于标记发送中、成功、失败等状态，适合以后扩展重试、流式输出、异常提示；time 表示这条消息生成的时间，用于展示发送时间，或者以后做消息排序与调试。


activeConversationId: string：当前会话 id
的作用是把“当前用户正在看哪一个会话”单独抽出来管理。因为系统里可能同时存在很多会话，但右侧聊天区一次只展示一个，所以必须有一个明确的“当前焦点”。它的价值不在于存内容，而在于建立索引关系：通过 activeConversationId 去 conversationList 中查找对应会话，再拿到那个会话的 messageList 给对话框渲染。也就是说，它是连接“侧边栏选择行为”和“主聊天区显示内容”的桥梁。

数据流：
这个几个结构和在一起后，整个数据流会很清楚：新建对话时候，向conversationList追加一个新的Conversation；切换对话的时候，更新activeConversationId；发送消息时候，找到当前激活的COnversation，再向它的messageList里面追加一条message；机器人回复时，继续向同一个 messageList 追加新的消息；侧边栏展示时，读取的是 conversationList；聊天窗口展示时，读取的是当前会话的 messageList。所以从本质上讲，这套核心数据结构就是在解决一句话：“当前用户在多个会话里，正在看哪一个会话，以及这个会话里有哪些消息。”

## 2026.3.21_11:04 之后规划

### UI组件
### 数据库的处理
### 前端发送的结构 & 后端返回的结构
{
  "conversationId": "conv_001",
  "message": {
    "role": "user",
    "content": "帮我解释这段代码"
  },
  "history": [
    { "role": "user", "content": "xxx" },
    { "role": "assistant", "content": "xxx" }
  ]
}

{
  "message": {
    "id": "msg_002",
    "role": "assistant",
    "content": "这是回复内容",
    "time": "2026-03-21T10:00:00Z"
  }
}

### 声明

当前版本为单用户前端聊天框架，消息与会话仅在当前页面实例中维护，不包含登录、身份识别、用户隔离与多用户会话管理能力。

当前前端仅在内存中维护会话与消息数据（conversationList / messageList），后端返回的数据会被追加到当前会话中，但不会持久化；页面刷新后状态会重置。如需保留数据，可扩展本地存储或接入后端数据库。


## 2026.4.14_11:50 接入接口

查看后端

先确认后端地址
再在前端发请求
最后处理跨域和字段对齐

### 第一步：先找后端接口

请求

方法：POST
地址：http://localhost:8326/ask

```JSON
{
  "question": "string",
  "context": "None",
  "is_search": false,
  "use_neural_retrieval": false
}
```

返回

string

### 第二步：整理文件

前端文件(Vue3)

index.html; 入口HTML
vite.config.js; Vite构建配置
package.json; 前端依赖与脚本
src/main.js; Vue应用入口
src/App.vue; 根组件
src/style.css; 全局样式
src/components/Sidebar.vue; 侧边栏组件
src/components/Welcome.vue; 欢迎提示语组件


后端文件与前端有关（FastAPI + RAG）

executed.py; 后端入口，FastAPI应用，定义 /ask 接口

其他
.gitigore; Git 忽略规则
readme.md; 项目说明
dist/; 前端构建产物
node_modules/; 前端依赖包
__pycache__/; Python编译缓存


### 第三步：连接

前端所有状态都集中在 App.vue 中管理

要改3个函数：

1. requestAssistantReply 完全重写

  从 response.json() 一次性读取 → 改为 response.body.getReader()             
  逐块读取流式响应，每个 token 通过回调传出。

2. handleSendMessage — 修改调用方式

  原来等完整回复再 pushMessage 一次 → 改为先 pushMessage 一条空的 assistant
  消息，然后流式接收过程中不断追加内容到这条消息。

3. extractAssistantContent — 可以删掉

  流式返回的是纯文本 token，不再是 JSON 对象，这个解析函数不再需要

跑通

### 第四步：增加神经检索模式

  ChatWindow.vue                                                             
                                                                           
  - 新增 searchMode ref 状态                                               
  - 输入框左侧加了 Search 切换按钮（OFF 时灰色，ON 时蓝色高亮）              
  - onSend() emit 时带上 searchMode
  - Welcome 示例点击也带上 searchMode                                        
                                                                           
  App.vue                                                                    

  - handleSendMessage(content, searchMode) — 接收第二个参数
  - buildRequestPayload(conversation, text, searchMode) — is_search
  由参数控制
  - requestAssistantReply(conversation, text, onToken, searchMode) — 传递到
  payload                                                                    
   
  数据流：                                                                   
  用户点 Search 按钮 → searchMode 取反                      
  用户发送消息 → emit('send', text, searchMode)
  → handleSendMessage(text, searchMode)
  → buildRequestPayload → { is_search: searchMode }
  → 后端收到 is_search: true/false


### 第五步：修复侧边栏bug

改动完成，总结：                                                           
                                      
  Bug 修复：删除会话循环创建                                                 
                                                                           
  handleRemoveConversation 中，原来删完列表为空会 createConversation
  创建新对话 → 新对话出现 → 再删又创建。现在改为只置空                       
  activeConversationId，不再自动创建。
                                                                             
  侧边栏折叠                                                

  ┌─────────────┬─────────────────────────────────────────────────────────┐
  │    文件     │                          改动                           │
  ├─────────────┼─────────────────────────────────────────────────────────┤
  │ Sidebar.vue │ 新增 collapsed prop，折叠时只显示 > 按钮，展开时显示 <  │
  │             │ + 完整内容                                              │
  ├─────────────┼─────────────────────────────────────────────────────────┤
  │ App.vue     │ 新增 sidebarCollapsed 状态，布局宽度通过 v-bind         │
  │             │ 动态切换 280px / 48px，带 0.2s 过渡动画                 │  
  └─────────────┴─────────────────────────────────────────────────────────┘
                                                                             
  折叠/展开操作：点击侧边栏上的 < / > 按钮切换。 

  ⏺ 改完了。现在的行为：
                                                                             
  - 大屏幕：侧边栏正常显示，点击 < 可手动折叠                                
  - **小屏幕 (<=920px)**：自动折叠成左侧一个 > 按钮，布局始终是左右结构（48px
   + 1fr），不会跑到顶部
                                                                             
  如果你想在小屏时展开侧边栏查看会话列表，点 > 按钮就行。


扩大回答的字数限制  


## 2026.4.14_13:32 基本完成要求