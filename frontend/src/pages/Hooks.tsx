export default function Hooks() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Hook Generator</h1>
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600">Generate engaging hooks for your content.</p>
        <div className="mt-4">
          <textarea
            className="w-full h-32 p-4 border rounded-lg"
            placeholder="Enter your content idea here..."
          />
          <button className="mt-4 px-4 py-2 bg-primary-600 text-white rounded hover:bg-primary-700">
            Generate Hooks
          </button>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Short Hooks (15-30s)</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• "You don't hate people, you're overstimulated."</li>
            <li>• "That thing you've been avoiding? It needs attention."</li>
            <li>• "This is your sign to rest, not quit."</li>
          </ul>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="font-semibold mb-2">Carousel Hooks</h3>
          <ul className="space-y-2 text-sm text-gray-600">
            <li>• "5 signs you're actually burnt out, not lazy"</li>
            <li>• "Things I wish I knew about ADHD"</li>
            <li>• "Your brain isn't broken: a thread"</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
