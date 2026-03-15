// Module: extensions/IframeExtension.ts | Agent: frontend-agent | Task: p44_frontend_iframe_extension
import { Node, mergeAttributes } from '@tiptap/core'

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    iframe: {
      setIframe: (options: {
        src: string
        width?: string
        height?: string
        allowfullscreen?: boolean
        allow?: string
      }) => ReturnType
    }
  }
}

export const IframeExtension = Node.create({
  name: 'iframe',
  group: 'block',
  atom: true,
  draggable: true,

  addAttributes() {
    return {
      src: { default: null },
      width: { default: '100%' },
      height: { default: '400px' },
      frameborder: { default: '0' },
      allowfullscreen: {
        default: true,
        parseHTML: (element: Element) => element.hasAttribute('allowfullscreen'),
        renderHTML: (attributes: Record<string, unknown>) => {
          if (!attributes.allowfullscreen) return {}
          return { allowfullscreen: 'true' }
        },
      },
      allow: {
        default:
          'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture',
      },
      scrolling: { default: null },
      style: { default: null },
    }
  },

  parseHTML() {
    return [{ tag: 'iframe[src]' }]
  },

  renderHTML({ HTMLAttributes }) {
    return [
      'div',
      { class: 'iframe-wrapper' },
      ['iframe', mergeAttributes({ frameborder: '0' }, HTMLAttributes)],
    ]
  },

  addNodeView() {
    return ({ node }) => {
      const wrapper = document.createElement('div')
      wrapper.className = 'iframe-wrapper'

      const iframe = document.createElement('iframe')
      iframe.src = (node.attrs.src as string) || ''
      iframe.width = (node.attrs.width as string) || '100%'
      iframe.frameBorder = '0'

      if (node.attrs.style) {
        iframe.style.cssText = node.attrs.style as string
      }
      if (node.attrs.height) {
        iframe.style.height = node.attrs.height as string
      }
      if (node.attrs.allowfullscreen) {
        iframe.setAttribute('allowfullscreen', 'true')
      }
      if (node.attrs.allow) {
        iframe.allow = node.attrs.allow as string
      }
      if (node.attrs.scrolling) {
        iframe.scrolling = node.attrs.scrolling as string
      }

      wrapper.appendChild(iframe)

      return { dom: wrapper }
    }
  },

  addCommands() {
    return {
      setIframe:
        (options) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: options,
          })
        },
    }
  },
})
